class CliError(Exception):
    """Raised when a cli command throws an error."""
    pass


class ImgDownloadError(Exception):
    """Raised when a specific image failed to download."""
    pass


class InstallationError(Exception):
    """Raised when some error ocurred during a program installation."""
    pass


class UnexistentPathError(Exception):
    """Raised when a path to a specific directory does not exist."""
    pass

