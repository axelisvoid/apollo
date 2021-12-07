from typing import List, Optional, Tuple
from cli import cmd_concat, comm


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


def install_apt_pkgs() -> Tuple[bool, Optional[str]]:
    """Installs apt packages.

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    pkgs = list_apt_pkgs()
    pkgs_ = " ".join(pkgs)
    cmd = f"apt install -y {pkgs_}"

    _, stderr = comm(cmd)
    if stderr:
        return False, stderr
    return True, None


def install_snap_pkgs() -> Tuple[bool, Optional[str]]:
    """Installs snap pkgs.

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    pkgs = list_snap_pkgs()

    # separate any package that needs the `--classic` flag
    # for now it simply assumes that if there is a flag, it will be exactly the `--classic` flag
    # fortunately, all the snap pkgs I need either don't need a flag or the flag is `--classic`. For now.

    flg_pkgs: List[str] = []
    for pkg in pkgs:
        flag = "--classic"
        if flag in pkg:
            flg_pkgs.append(pkg)
            pkgs.remove(pkg)

    install_cmd = "snap install"
    for flg_pkg in flg_pkgs:
        flg_pkg = install_cmd + flg_pkg

    pkgs_ = " ".join(pkgs)
    cmd1 = f"snap install {pkgs_}"

    _, stderr = comm(cmd1)
    if stderr:
        return False, stderr

    cmd2 = cmd_concat(flg_pkgs)

    _, stderr = comm(cmd2)
    if stderr:
        return False, stderr

    return True, None


def install_brave_browser() -> Tuple[bool, Optional[str]]:
    """Installs Brave Browser.

    Installation instructions from <https://brave.com/linux/#linux>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """

    cmd = ("sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg "
    "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
           )

    _, stderr = comm(cmd)
    if stderr:
        return False, stderr

    cmd = ("echo "
           "\"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] "
           "https://brave-browser-apt-release.s3.brave.com/ stable main\""
           " | "
           "sudo tee /etc/apt/sources.list.d/brave-browser-release.list"
          )

    _, stderr = comm(cmd)
    if stderr:
        return False, stderr

    cmd = "update -y && install -y brave-browser"

    _, stderr = comm(cmd)
    if stderr:
        return False, stderr

    return True, None


def install_docker() -> Tuple[bool, Optional[str]]:
    """Installs Docker Engine and Docker Compose v2.

    Installation instructions from <https://docs.docker.com/engine/install/ubuntu/> and
    <https://docs.docker.com/engine/install/linux-postinstall/>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """


    cmd1 = ("curl -fsSL https://download.docker.com/linux/ubuntu/gpg"
           " | "
           "sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
          )

    cmd2 = ("echo "
            "\"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] "
            "https://download.docker.com/linux/ubuntu "
            "$(lsb_release -cs) stable\""
            " | "
            "sudo tee /etc/apt/sources.list.d/docker.list > /dev/null"
           )

    cmd = cmd_concat([cmd1, cmd2])

    _, stderr = comm(cmd)
    if stderr:
        return False, stderr

    cmd = "apt update -y && apt install docker-ce docker-ce-cli containerd.io"
    _, stderr = comm(cmd)
    if stderr:
        return False, stderr

    # post-install step required for all Linux distros

    cmd = "groupadd docker && usermod -aG docker $USER"
    _, stderr = comm(cmd)
    if stderr:
        return False, stderr

    return True, None


def install_fish_shell():
    """Installs Fish Shell.

    Installation instructions from <https://launchpad.net/~fish-shell/+archive/ubuntu/release-3>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """


def install_google_chrome():
    """Installs Google Chrome.

    [No installation "instructions" for Google Chrome]

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """


def install_poetry():
    """Installs Poetry (package manager for Python).

    Installation instructions from <https://python-poetry.org/docs/>

    Returns
    -------
    bool, str or None
        Tuple representing the status of the installation, and the error message if there was any (None otherwise).
    """


# testing installation commands
if __name__ == "__main__":

    install_apt_pkgs()
    install_snap_pkgs()
    install_brave_browser()
    install_docker()
