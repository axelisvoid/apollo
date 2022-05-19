class EmptyCommandError(Exception):
    """Raised when an empty string is passed as a cli command."""
    pass


class CliError(Exception):
    """Raised when a cli command throws an error."""
    pass


class ImgDownloadError(Exception):
    """Raised when a specific image failed to download."""
    pass


class InstallationError(Exception):
    """Raised when some error ocurred during a program installation."""
    pass


class NotSupportedMachineError(Exception):
    """Raised when the machine running Apollo is not supported by it."""
    pass


class UnexistentPathError(Exception):
    """Raised when a path to a specific directory does not exist."""
    pass

