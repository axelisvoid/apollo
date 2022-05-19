from typing import Optional
#import argparse
import pathlib
import re
import subprocess as subp


class InstallationError(Exception):
  """Raised when if an error ocurred during a software installation."""
  pass


class RootUserExpectedError(Exception):
  """Raised when trying to run a command as a non-root user when a root user is expected."""
  pass


def isroot() -> bool:
  """Checks if the user running the script is root."""

  exec_path = pathlib.Path.home()
  
  if "root" in str(exec_path): return True
  return False


def comm(cmd: str) -> tuple[bytes, Optional[bytes]]:
  """Executes a terminal command."""

  cmd_ = cmd.split(" ")

  with subp.Popen(cmd_, stdout=subp.PIPE, stderr=subp.PIPE) as proc:
    try:
      outs, errs = proc.communicate()
    except KeyboardInterrupt:
      proc.kill()
      raise KeyboardInterrupt from KeyboardInterrupt

  return outs, errs


def rmstr(string: bytes, text: bytes) -> bytes:
  """Removes all ocurrences of a string from a text."""

  if string not in text:
    return text

  d_string = string.decode()
  d_text = text.decode()

  patt = re.compile(d_string)
  # the if stmt above takes care of the AttributeError warning on calling span() on possible NoneType
  res = patt.search(d_text).span()

  # delete string found from the text
  newtext = d_text.replace(d_text[res[0]:res[1]], "")

  return rmstr(string, bytes(newtext, "utf8"))


def rm_apt_warning(output: bytes) -> bytes:
  """Removes a typical apt cli warning from stderr message."""

  warning_msg = b"\nWARNING: apt does not have a stable CLI interface. Use with caution in scripts.\n\n"
  return rmstr(warning_msg, output)


def install_apt_pkgs() -> bool:
  """Installs apt packages."""

  pkgs = [
    
    # for development
    "build-essential",
    "python3-dev",
    "pkg-config",

    # useful to have
    "apt-transport-https",
    "cmake",
    "curl",
    "ca-certificates",
    "gnupg",
    "lsb-release",

    # miscellaneous
    "htop",
    "mmv",
    "neovim",
    "tmux",

  ]

  cmd = "apt install -y" + " ".join(pkgs)
  _, errs = comm(cmd)
  if errs:
    raise InstallationError("Failed to install apt packages.")
  return True


def install_snap_pkgs() -> bool:
  """Installs snaps."""

  pkgs = [
    "bitwarden",
    "jdownloader2",
    "lireoffice",
    "signal-desktop",
    "spotify",
    "vlc",

    "sublime-text --classic",
    "code --classic"
    "pycharm-community --classic"
  ]

  for pkg in pkgs:
    cmd = "snap install " + pkg
    _, errs = comm(cmd)
    if errs:
      raise InstallationError(f"Failed to install {pkg}")
  return True


def cleanup() -> bool:
  """Tidies up"""

  cleanups = [
    "apt autoclean && apt clean"
  ]

  for cmd in cleanups:
    _, errs_ = comm(cmd)
    if errs_ and rm_apt_warning(errs_):
      raise InstallationError("Failed in cleanup procedures. Manual cleanup may be necessary.")    
  
  return True


if __name__ == "__main__":
  pass