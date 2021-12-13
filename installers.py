from pathlib import Path
from shutil import which
from subprocess import TimeoutExpired
from typing import List, Optional, Tuple
from cli import capture_and_remove_apt_warning, cmd_concat, comm
from exceptions import InstallationError


CURRENT_PATH = Path.cwd()
DOWNLOADS_DIR = f"{CURRENT_PATH}/inst_downloads"


def list_apt_pkgs() -> List[str]:
    """Returns a list of apt packages to be installed."""

    pkgs = [
        # essential for development
        "build-essential",
        "python3-dev",
        "pkg-config",

        # needed for other software installation and/or they're simply useful
        "apt-transport-https",
        "curl",
        "ca-certificates",
        "gnupg",
        "lsb-release",

        # to build C/C++ code
        "ninja-build",

        # needed for OpenGL programming.
        "cmake",
        "mesa-utils",
        "libglu1-mesa-dev",
        "freeglut3-dev",
        "mesa-common-dev",
        "libglew-dev",
        "libglfw3-dev",
        "libglm-dev",
        "libao-dev",
        "libmpg123-dev",
        "xorg-dev",                     # X11-specific desktop environment

        "htop",                         # better than top
        "mmv",                          # move/copy/append/link multiple files according to a set of wildcard patterns
        "tmux",                         # terminal multiplexer

    ]

    return pkgs


def list_snap_pkgs() -> List[str]:
    """Returns a list of snap apps."""

    pkgs = [
        "bitwarden",
        "libreoffice",
        "signal-desktop",
        "spotify",
        "vlc",

        "sublime-text --classic",
        "code --classic",
    ]

    return pkgs


def install_apt_pkgs() -> bool:
    """Installs apt packages.

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    pkgs = list_apt_pkgs()
    pkgs_ = " ".join(pkgs)
    cmd = f"apt install -y {pkgs_}"

    _, errs_ = comm(cmd)
    errs = capture_and_remove_apt_warning(errs_)

    if errs:
        # print(errs)
        raise InstallationError("Apt packages were not installed.")
    return True


def install_snap_pkgs() -> bool:
    """Installs snap pkgs.

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    pkgs_ = list_snap_pkgs()
    install_cmd = "snap install "

    err_msg = "Snap packages were not installed."

    # separate any package that needs the `--classic` flag
    # for now it simply assumes that if there is a flag, it will be exactly the `--classic` flag
    # fortunately, all the snap pkgs I need either don't need a flag or the flag is `--classic`. For now.

    flg_pkgs: List[str] = []
    flag = "--classic"

    for i, val in enumerate(pkgs_):
        if flag in val:
            flg_pkg = install_cmd + pkgs_[i]
            flg_pkgs.append(flg_pkg)

    cmd = cmd_concat(flg_pkgs)

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    pkgs = " ".join(pkgs_)
    cmd = install_cmd + pkgs

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    return True


def install_brave_browser() -> bool:
    """Installs Brave Browser.

    Installation instructions from <https://brave.com/linux/#linux>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    err_msg = "Brave browser was not installed."

    cmd = ("curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg "
    "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
           )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    cmd = ("echo "
           "\"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] "
           "https://brave-browser-apt-release.s3.brave.com/ stable main\""
           " | "
           "tee /etc/apt/sources.list.d/brave-browser-release.list"
          )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    cmd = "apt update -y && apt install -y brave-browser"

    _, errs_ = comm(cmd)
    errs = capture_and_remove_apt_warning(errs_)
    if errs:
        raise InstallationError(err_msg)

    return True


def install_docker() -> bool:
    """Installs Docker Engine and Docker Compose v2.

    Installation instructions from <https://docs.docker.com/engine/install/ubuntu/> and
    <https://docs.docker.com/engine/install/linux-postinstall/>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    err_msg = "Docker was not installed."

    cmd = ("curl -fsSL https://download.docker.com/linux/ubuntu/gpg"
           " | "
           "gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
          )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)


    cmd = ("echo "
           "\"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] "
           "https://download.docker.com/linux/ubuntu "
           "$(lsb_release -cs) stable\""
           " | "
           "tee /etc/apt/sources.list.d/docker.list > /dev/null"
           )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    cmd = "apt update -y && apt install docker-ce docker-ce-cli containerd.io"

    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    # post-install step required for all Linux distros

    cmd = "groupadd docker && usermod -aG docker $USER"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    return True


def install_fish_shell() -> bool:
    """Installs Fish Shell.

    Installation instructions from <https://launchpad.net/~fish-shell/+archive/ubuntu/release-3>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    err_msg = "Fish shell was not installed."
    ppa_src = ("\"deb http://ppa.launchpad.net/fish-shell/release-3/ubuntu $(lsb_release -cs) main\n"
               "# deb-src http://ppa.launchpad.net/fish-shell/release-3/ubuntu $(lsb_release -cs) main\""
              )
    ppa_file_name = "fish-shell-ubuntu-release-3-$(lsb_release -cs).list"

    cmd = f"echo {ppa_src} >> {ppa_file_name}"
    _, errs = comm(cmd)
    if errs:
        raise IntallationError(err_msg)

    fingerprint = "59FDA1CE1B84B3FAD89366C027557F056DC33CA5"
    cmd = f"apt-key adv --keyserver keyserver.ubuntu.com --recv-keys {fingerprint}"
    _, errs = comm(cmd)
    if errs:
        raise IntallationError(err_msg)

    cmd = "apt update -y && install -y fish"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    return True


def install_google_chrome() -> bool:
    """Installs Google Chrome.

    [No installation "instructions" for Google Chrome]

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    err_msg = "Google Chrome was not installed."

    file_name = "google-chrome-stable_current_amd64.deb"
    file_url = f"https://dl.google.com/linux/direct/{file_name}"
    cmd = f"cd {DOWNLOADS_DIR} && curl -O {file_url}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    cmd = "apt install -y ./{file_name}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    cmd = f"rm {file_name}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    return True


def install_poetry() -> bool:
    """Installs Poetry (package manager for Python).

    Installation instructions from <https://python-poetry.org/docs/>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    err_msg = "Poetry was not installed."

    python_v = ""
    if which("python3"):
        python_v = "3"
    cmd = f"curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python{python_v} -"
    _, errs = comm(cmd)
    if errs:
        InstallationError(err_msg)

    return True

def install_not_ppkd_prog() -> bool:
    """Installs all programs not in apt nor snap packages."""

    # brave browser
    try:
        install_brave_browser()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Brave browser was not installed") from InstallationError
        raise InstallationError("Brave browser installation took to long to complete.") from TimeoutExpired

    # docker
    try:
        install_docker()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Docker was not installed.")
        raise InstallationError("Docker installation took to long to complete.") from TimeoutExpired

    # fish shell
    try:
        install_fish_shell()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Fish shell was not installed.")
        raise InstallationError("Fish shell installation took to long to complete.") from TimeoutExpired

    # google chrome
    try:
        install_google_chrome()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Google Chrome was not installed.") from InstallationError
        raise InstallationError("Google Chrome installation took to long to complete.") from TimeoutExpired

    # poetry
    try:
        install_poetry()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Poetry was not installed.") from InstallationError
        raise InstallationError("Poetry installation took to long to complete.") from TimeoutExpired

    return True


# testing installation commands
if __name__ == "__main__":

    # install_apt_pkgs()
    # install_snap_pkgs()
    # install_not_ppkd_prog()

