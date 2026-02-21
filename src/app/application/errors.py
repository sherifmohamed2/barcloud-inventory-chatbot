"""
Application-layer exceptions.
"""

from src.app.domain.errors import BarCloudError


class ApplicationError(BarCloudError):
    """Base for all application-layer exceptions."""
