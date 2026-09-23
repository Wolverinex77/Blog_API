"""Application-specific exception types."""


class EmailAlreadyExistsError(Exception):
    """Raised when a user attempts to register an email that is already in use."""


class InvalidCredentialsError(Exception):
    """Raised when supplied authentication credentials are invalid."""


class UserNotFound(Exception):
    """Raised when the authenticated user cannot be found."""


class PostNotFound(Exception):
    """Raised when a post cannot be found."""


class PostSlugAlreadyExists(Exception):
    """Raised when a generated post slug is already in use."""

class CommentNotFound(Exception):
    """Raised when a comment cannot be found."""


class GeminiResponseError(Exception):
    """Raised when Gemini does not return a usable response."""


class LikeNotFound(Exception):
    """Raised when a like cannot be found."""


class CategoryNotFound(Exception):
    """Raised when a category cannot be found."""


class CategoryAlreadyExists(Exception):
    """Raised when a category name is already in use."""


class CategoryInUse(Exception):
    """Raised when a category still has posts assigned to it."""


class TagAlreadyExists(Exception):
    """Raised when a tag name is already in use."""

class InvalidImageTypeError(Exception):
    """Raised when an uploaded image has an unsupported MIME type."""


class ImageTooLargeError(Exception):
    """Raised when an uploaded image exceeds the maximum allowed size."""


class InvalidImageError(Exception):
    """Raised when an uploaded file is not a valid image."""


class ImageFormatError(Exception):
    """Raised when an image format cannot be determined or is unsupported."""


class EmailAlreadyInUseError(Exception):
    """Raised when an update uses an email already assigned to another user."""


class UserNameAlreadyExistsError(Exception):
    """Raised when a user attempts to register a username that is already in use."""
