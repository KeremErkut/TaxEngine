from decimal import Decimal
from datetime import date, timedelta

from src.models.trade import Trade, TradeType
from src.models.fifo_lot import FifoLot
from src.models.gain_record import GainRecord
from src.engine.reference_service import ReferenceDataService


class FifoEngine:
    """
    Chronological FIFO matching engine.
    Processes sorted Trade list, maintains active lots,
    and produces GainRecord list for tax calculation.
    """

    def __init__(self, ref_service: ReferenceDataService, config: dict) -> None:
        self._ref_service = ref_service
        self.config = config
        self._wpi_threshold = Decimal("1") + config["indexing"]["wpi_threshold"]
        self._active_lots: list[FifoLot] = []
        self._gain_records: list[GainRecord] = []

    def process(self, trades: list[Trade]) -> list[GainRecord]:
        """
        Main processing loop. Trades must be sorted by date ascending.
        CSVLoader guarantees this order.
        """
        for trade in trades:
            if trade.trade_type == TradeType.BUY:
                self._handle_buy(trade)
            else:
                self._handle_sell(trade)

        return self._gain_records

    def _handle_buy(self, trade: Trade) -> None:
        rate = self._ref_service.get_rate(trade.trade_date)
        cost_basis_tl = trade.quantity * trade.price_fc * rate

        lot = FifoLot(
            purchase_trade_id=trade.trade_id,
            ticker=trade.ticker,
            original_qty=trade.quantity,
            remaining_qty=trade.quantity,
            cost_basis_tl=cost_basis_tl,
            purchase_date=trade.trade_date,
        )

        self._active_lots.append(lot)

    def _previous_month(self, d: date) -> tuple[int, int]:
        """
        Clean previous month calculation.
        Using datetime arithmetic prevents year rollover bugs.
        """
        first_day = d.replace(day=1)
        prev_day = first_day - timedelta(days=1)
        return prev_day.year, prev_day.month

    def _handle_sell(self, trade: Trade) -> None:
        sell_rate = self._ref_service.get_rate(trade.trade_date)
        sell_price_tl = trade.price_fc * sell_rate
        shares_to_sell = trade.quantity

        while shares_to_sell > Decimal("0"):
            if not self._active_lots:
                raise ValueError(
                    f"Active lot not found: {trade.ticker} "
                    f"sell date={trade.trade_date}, qty={shares_to_sell}"
                )

            lot = self._active_lots[0]

            # Clean previous-month calculation (fixes January → December year rollover)
            sell_year, sell_month = self._previous_month(trade.trade_date)
            buy_year, buy_month = self._previous_month(lot.purchase_date)

            sell_wpi = self._ref_service.get_wpi(sell_year, sell_month)
            buy_wpi = self._ref_service.get_wpi(buy_year, buy_month)

            index_ratio = sell_wpi / buy_wpi
            is_indexed = index_ratio >= self._wpi_threshold

            unit_cost_tl = lot.cost_basis_tl / lot.original_qty
            adjusted_unit_cost_tl = (
                unit_cost_tl * index_ratio if is_indexed else unit_cost_tl
            )

            matched_qty = min(shares_to_sell, lot.remaining_qty)
            unit_gain = sell_price_tl - adjusted_unit_cost_tl
            total_gain = unit_gain * matched_qty

            audit_note = (
                f"WPI ratio: {index_ratio:.4f} "
                f"{'(indexing applied)' if is_indexed else '(no indexing)'} | "
                f"buy_wpi={buy_wpi} sell_wpi={sell_wpi}"
            )

            self._gain_records.append(
                GainRecord(
                    sell_trade_id=trade.trade_id,
                    ticker=trade.ticker,
                    matched_qty=matched_qty,
                    realized_gain_tl=total_gain,
                    is_indexed=is_indexed,
                    audit_note=audit_note,
                )
            )

            updated_lot = lot.consume(matched_qty)
            self._active_lots[0] = updated_lot

            if updated_lot.is_depleted():
                self._active_lots.pop(0)

            shares_to_sell -= matched_qty