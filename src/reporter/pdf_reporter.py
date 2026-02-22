from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from src.models.gain_record import GainRecord

TWO_PLACES = Decimal("0.01")


class PDFReporter:
    """
    Generates a formatted .pdf compliance report.
    Contains Annual Tax Summary and Transaction Audit List.
    """

    HEADER_COLOR = colors.HexColor("#2E75B6")
    GAIN_COLOR = colors.HexColor("#008000")
    LOSS_COLOR = colors.HexColor("#FF0000")
    LIGHT_GRAY = colors.HexColor("#F2F2F2")

    def generate(
        self,
        summary: dict,
        records: list[GainRecord],
        output_path: str = "output_report.pdf",
    ) -> str:

        path = Path(output_path)
        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            textColor=self.HEADER_COLOR,
            fontSize=16,
            spaceAfter=12,
        )
        story.append(Paragraph("TaxEngine — Annual Tax Report", title_style))
        story.append(Paragraph(f"Fiscal Year: {summary['fiscal_year']}", styles["Normal"]))
        story.append(Spacer(1, 0.5 * cm))

        # Summary table
        story.append(Paragraph("Tax Summary", styles["Heading2"]))
        story.append(Spacer(1, 0.3 * cm))
        story.append(self._build_summary_table(summary))
        story.append(Spacer(1, 0.8 * cm))

        # Audit table
        story.append(Paragraph("Transaction Audit List", styles["Heading2"]))
        story.append(Spacer(1, 0.3 * cm))
        story.append(self._build_audit_table(records))

        disclamer_style = ParagraphStyle(
            "Disclaimer",
            parent=styles["Normal"],
            textColor=colors.red,
            fontSize=9,
            italics=True,
            spaceBefore=20,
        )
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph(
            "Advisory only. Consult a tax professional for offical filing.",
            disclamer_style
        ))

        doc.build(story)
        return str(path)

    def _build_summary_table(self, summary: dict) -> Table:
        rows = [
            ["Metric", "Value"],
            ["Total Gain (TL)", self._fmt(summary["total_gain_tl"])],
            ["Total Loss (TL)", self._fmt(summary["total_loss_tl"])],
            ["Net Gain (TL)", self._fmt(summary["net_gain_tl"])],
            ["Exemption Applied (TL)", self._fmt(summary["exemption_applied_tl"])],
            ["Taxable Base (TL)", self._fmt(summary["taxable_base_tl"])],
            ["Estimated Tax (TL)", self._fmt(summary["estimated_tax_tl"])],
        ]

        table = Table(rows, colWidths=[10 * cm, 6 * cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), self.HEADER_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (1, -1), "RIGHT"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))
        return table

    def _build_audit_table(self, records: list[GainRecord]) -> Table:
        headers = ["Ticker", "Qty", "Gain/Loss (TL)", "Indexed", "WPI Ratio"]
        rows = [headers]

        for record in records:
            wpi_ratio = record.audit_note.split("|")[0].replace("WPI ratio:", "").strip()
            rows.append([
                record.ticker,
                str(record.matched_qty),
                self._fmt(record.realized_gain_tl),
                "Yes" if record.is_indexed else "No",
                wpi_ratio,
            ])

        table = Table(rows, colWidths=[2.5 * cm, 2 * cm, 4 * cm, 2 * cm, 5.5 * cm])

        style = [
            ("BACKGROUND", (0, 0), (-1, 0), self.HEADER_COLOR),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, self.LIGHT_GRAY]),
        ]

        # Kazanç yeşil, zarar kırmızı
        for i, record in enumerate(records, start=1):
            color = self.GAIN_COLOR if record.realized_gain_tl >= 0 else self.LOSS_COLOR
            style.append(("TEXTCOLOR", (2, i), (2, i), color))

        table.setStyle(TableStyle(style))
        return table

    def _fmt(self, value: Decimal) -> str:
        """Formats Decimal to human-readable string with 2 decimal places."""
        rounded = value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)
        return f"{rounded:,}"