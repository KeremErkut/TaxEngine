from abc import ABC, abstractmethod

from src.models.trade import Trade

class DataSource():
    """
    Abstract base class for all data sources adapters
    Future Implementation: CSVDataSource, APIDataSource, etc.
    """

    @abstractmethod
    def load(self, source:str) -> list[Trade]: # Python 3.9+ native generics
        """
        Load and return a list of validated Trade objects.

        :param source: File path, URL, or connection string.
        :raises ValueError: If source is invalid or data cannot be parsed.
        :returns: List of Trade objects sorted by trade_date ascending.
        """
        pass