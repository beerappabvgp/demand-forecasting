class ForecastingException(Exception):
    """Base exception for project."""
    pass


class DatasetNotFoundException(ForecastingException):
    """Raised when dataset is missing."""
    pass
