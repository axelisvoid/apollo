from pathlib import Path
from shutil import copyfile, SameFileError, which
from subprocess import TimeoutExpired
from typing import List, Optional, Tuple
from cli import capture_and_remove_apt_warning, cmd_concat, comm
from exceptions import InstallationError


HOME_PATH = str(Path.home())
CURRENT_PATH = str(Path.cwd())
CONFIG_FILES_PATH = f"{CURRENT_PATH}/files"
DOWNLOADS_PATH = f"{CURRENT_PATH}/inst_downloads"


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


def pre_install() -> bool:
    """Creates "downloads" directory to be used at any point during the installation and post-installation phase."""

    cmd = f"mkdir {DOWNLOADS_DIR}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed pre-installation procedure.")
    return True


def install_apt_pkgs() -> bool:
    """Installs apt packages."""

    pkgs = list_apt_pkgs()
    pkgs_ = " ".join(pkgs)
    cmd = f"apt install -y {pkgs_}"

    _, errs_ = comm(cmd)
    errs = capture_and_remove_apt_warning(errs_)

    if errs:
        raise InstallationError("Apt packages were not installed.")
    return True


def install_snap_pkgs() -> bool:
    """Installs snap pkgs."""

    pkgs_ = list_snap_pkgs()
    install_cmd = "snap install "

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
        raise InstallationError("Failed to install flagged snaps.")

    pkgs = " ".join(pkgs_)
    cmd = install_cmd + pkgs

    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install unflagged snaps.")

    return True


def install_brave_browser() -> bool:
    """Installs Brave Browser.

    Installation instructions from <https://brave.com/linux/#linux>.
    """

    cmd = ("curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg "
    "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
           )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Brave Browser's fingerprint.")

    cmd = ("echo "
           "\"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] "
           "https://brave-browser-apt-release.s3.brave.com/ stable main\""
           " | "
           "tee /etc/apt/sources.list.d/brave-browser-release.list"
          )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Brave Browser's ppa.")

    cmd = "apt update -y && apt install -y brave-browser"

    _, errs_ = comm(cmd)
    errs = capture_and_remove_apt_warning(errs_)
    if errs:
        raise InstallationError("Failed to install Brave Browser's apt package.")

    return True


def install_docker() -> bool:
    """Installs Docker Engine and Docker Compose v2.

    Installation instructions from <https://docs.docker.com/engine/install/ubuntu/> and
    <https://docs.docker.com/engine/install/linux-postinstall/>
    """

    cmd = ("curl -fsSL https://download.docker.com/linux/ubuntu/gpg"
           " | "
           "gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg"
          )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Docker's fingerprint.")


    cmd = ("echo "
           "\"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] "
           "https://download.docker.com/linux/ubuntu "
           "$(lsb_release -cs) stable\""
           " | "
           "tee /etc/apt/sources.list.d/docker.list > /dev/null"
           )

    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Docker's ppa.")

    cmd = "apt update -y && apt install docker-ce docker-ce-cli containerd.io"

    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install Docker apt packages.")

    # post-install step required for all Linux distros

    cmd = "groupadd docker && usermod -aG docker $USER"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Docker's group and/or add user to Docker's group.")

    return True


def install_fish_shell() -> bool:
    """Installs Fish Shell.

    Installation instructions from <https://launchpad.net/~fish-shell/+archive/ubuntu/release-3>
    """

    ppa_src = ("\"deb http://ppa.launchpad.net/fish-shell/release-3/ubuntu $(lsb_release -cs) main\n"
               "# deb-src http://ppa.launchpad.net/fish-shell/release-3/ubuntu $(lsb_release -cs) main\""
              )
    ppa_file_name = "fish-shell-ubuntu-release-3-$(lsb_release -cs).list"

    cmd = f"echo {ppa_src} >> {ppa_file_name}"
    _, errs = comm(cmd)
    if errs:
        raise IntallationError("Failed to create Fish's ppa file.")

    fingerprint = "59FDA1CE1B84B3FAD89366C027557F056DC33CA5"
    cmd = f"apt-key adv --keyserver keyserver.ubuntu.com --recv-keys {fingerprint}"
    _, errs = comm(cmd)
    if errs:
        raise IntallationError("Failed to add Fish's fingerprint.")

    cmd = "apt update -y && install -y fish"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install Fish shell.")

    return True


def install_google_chrome() -> bool:
    """Installs Google Chrome."""

    err_msg = "Google Chrome was not installed."

    file_name = "google-chrome-stable_current_amd64.deb"
    file_url = f"https://dl.google.com/linux/direct/{file_name}"
    cmd = f"cd {DOWNLOADS_DIR} && curl -O {file_url}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to download Google Chrome's .deb file.")

    cmd = "apt install -y ./{file_name}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install Google Chrome from .deb file.")

    return True


def install_neovim() -> bool:
    """Installs Neovim.

    Installation instructions form <>"
    """

    url = "https://github.com/neovim/neovim/releases/latest/download/nvim.appimage"
    cmd = f"cd {DOWNLOADS_DIR} && curl -LO {url}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError(err_msg)

    cmd = f"cd {DOWNLOADS_DIR} && -u $USER chmod u+x nvim.appimage"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to make nvim.appimage executable.")

    return True

def install_poetry() -> bool:
    """Installs Poetry (package manager for Python).

    Installation instructions from <https://python-poetry.org/docs/>.
    """

    python_v = ""
    if which("python3"):
        python_v = "3"
    cmd = f"curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python{python_v} -"
    _, errs = comm(cmd)
    if errs:
        InstallationError("Poetry was not installed.")

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

    # neovim
    try:
        install_neovim()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Neovim was not installed.") from InstallationError
        raise InstallationError("Neovim installation took too long to complete.") from TimeoutExpired

    # poetry
    try:
        install_poetry()
    except InstallationError, TimeoutExpired:
        raise InstallationError("Poetry was not installed.") from InstallationError
        raise InstallationError("Poetry installation took to long to complete.") from TimeoutExpired

    return True


############################################ posts ###############################


def post_fish_shell() -> bool:
    """Sets fish as the default shell and copies fish functions to their configuration directory."""

    cmd = "-u $USER chsh -s `which fish`"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Fish shell's post installation procedure failed.")

    config_dest = f"{HOME_PATH}/.config/fish/functions"
    files = ["fish_greeting.fish", "fish_prompt.fish"]
    for file in files:
        src = f"{CONFIG_FILES_PATH}/fish/{file}"
        try:
            copyfile(src, f"{config_dest}/{file}")
        except SameFileError:
            raise SameFileError("The source and destination files are the same.") from SameFileError

    return True


def post_neovim() -> bool:
    """Sets up vim alias for nvim and copies `init.vim` file to configuration directory."""

    file = "nvim.appimage"
    src = f"{DOWNLOADS_DIR}/{file}"
    dest = f"/usr/local/bin/{file}"

    try:
        copyfile(src, dest)
    except SameFileError:
        raise SameFileError("The source and destination files are the same.") from SameFileError

    # make vim command execute nvim
    cmd = "update-alternatives --install /usr/bin/vim vim {dest} 110"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to create vim alias for neovim.")

    # copy `init.vim` to conf directory

    cmd = "mkdir ~/.config/neovim"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to create neovim config directory.")

    src = f"{CONFIG_FILES_PATH}/neovim/init.vim"
    dest = f"~/.config/neovim/init.vim"
    try:
        copyfile(src, dest)
    except SameFileError:
        raise SameFileError("The source and destination files are the same.") from SameFileError

    return True


def post_tmux() -> bool:
    """Fetches Tmux Plugin Manager and copies `.tmux.conf` file to `HOME_PATH`."""

    tpm_repo = "https://github.com/tmux-plugins/tpm"        # tpm repo url
    tpm_clone_path = "~/.tmux/plugins/tpm"                  # tpm repo dest path
    src = f"{CONFIG_FILES_PATH}/tmux.conf"                  # tmux.conf source path
    dest = "~/.tmux.conf"                                   # tmux.conf dest path

    # clone Tmux Plugin Manager github repo
    cmd = f"git clone {tpm_repo} {tpm_clone_path}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to clone Tmux Plugin Manager's github repo.")

    # copy .tmux.conf file
    try:
        copyfile(tmux_conf_src, tmux_conf_dest)
    except SameFileError:
        raise SameFileError("The source and destination files are the same.") from SameFileError

    return True


def post_install() -> bool:
    """Procedures that should occur after all programs have been installed."""

    try:
        post_fish_shell()
    except InstallationError:
        raise InstallationError("Fish shell's post installation procedures failed.")
    try:
        post_neovim()
    except InstallationError:
        raise InstallationError("Neovim's post installation procedures failed.")
    try:
        post_tmux()
    except InstallationError:
        raise InstallationError("Tmux's post installation procedures failed.")

    return True


def cleanup() -> bool:
    """Removes Downloads directory and apt cleans and apt autocleans the system."""

    cmd = f"rm -r {DOWNLOADS_PATH}"
    _, errs = comm(cmd)
    if errs:
        return False

    cmd = "apt autoclean && apt clean"
    _, errs = comm(cmd)
    if errs:
        return False

    return True


# testing installation commands
if __name__ == "__main__":

    # pre_install()
    # install_apt_pkgs()
    # install_snap_pkgs()
    # install_not_ppkd_prog()
    # post_install()
    # cleanup()

