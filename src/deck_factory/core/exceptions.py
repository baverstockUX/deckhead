"""
Custom exceptions for Deckhead.

Defines exception hierarchy for different error scenarios
to enable appropriate error handling and user-friendly messages.
"""


class DeckFactoryError(Exception):
    """Base exception for all Deck Factory errors."""
    pass


# Configuration Errors
class ConfigError(DeckFactoryError):
    """Base exception for configuration errors."""
    pass


class MissingAPIKeyError(ConfigError):
    """Raised when Gemini API key is missing."""
    pass


class InvalidAPIKeyError(ConfigError):
    """Raised when Gemini API key is invalid."""
    pass


# Input Errors
class InputError(DeckFactoryError):
    """Base exception for input errors."""
    pass


class FileNotFoundError(InputError):
    """Raised when a required file is not found."""
    pass


class InvalidFormatError(InputError):
    """Raised when a file has an invalid format."""
    pass


class EmptyContentError(InputError):
    """Raised when content file is empty."""
    pass


# API Errors
class APIError(DeckFactoryError):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded."""
    pass


class QuotaExceededError(APIError):
    """Raised when API quota is exceeded."""
    pass


class GenerationFailedError(APIError):
    """Raised when content/image generation fails."""
    pass


class InvalidResponseError(APIError):
    """Raised when API returns an invalid response."""
    pass


# Assembly Errors
class AssemblyError(DeckFactoryError):
    """Base exception for deck assembly errors."""
    pass


class ImageProcessingError(AssemblyError):
    """Raised when image processing fails."""
    pass


class SlideCreationError(AssemblyError):
    """Raised when slide creation fails."""
    pass
