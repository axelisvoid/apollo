from pathlib import Path
from shutil import copyfile, SameFileError, which
from subprocess import TimeoutExpired
from typing import List
from cli import capture_and_remove_apt_warning, comm
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

        # needed for OpenGL programming.
        "cmake",

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

    cmd = f"mkdir {DOWNLOADS_PATH}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed pre-installation procedure.")
    return True


def install_apt_pkgs() -> bool:
    """Installs apt packages."""

    pkgs = list_apt_pkgs()

    print("Installing Apt packages...")

    for pkg in pkgs:
        print("Installing {pkg}")
        _, errs_ = comm(f"apt install -y {pkg}")
        if errs_:
            errs = capture_and_remove_apt_warning(errs_)
            if errs:
                raise InstallationError(f"Failed to install {pkg}.")

    print("Apt packages successfully installed.")
    return True


def install_snap_pkgs() -> bool:
    """Installs snap pkgs."""

    pkgs_ = list_snap_pkgs()
    install_cmd = "snap install "

    # separate any package that needs the `--classic` flag
    # for now it simply assumes that if there is a flag, it will be exactly the `--classic` flag
    # fortunately, all the snap pkgs I need either don't need a flag or the flag is `--classic`. For now.

    unflg_pkgs: List[str] = []
    flg_pkgs: List[str] = []
    flag = "--classic"

    for pkg in pkgs_:
        if flag in pkg:
            flg_pkgs.append(pkg)
        else:
            unflg_pkgs.append(pkg)

    print("Installing Snap packages...")

    for pkg in flg_pkgs:
        print(f"Installing {pkg}...")
        _, errs = comm(f"{install_cmd} {pkg}")
        if errs:
            raise InstallationError(f"Failed to install {pkg}.")

    for pkg in unflg_pkgs:
        print(f"Installing {pkg}...")
        _, errs = comm(f"{install_cmd} {pkg}")
        if errs:
            raise InstallationError(f"Failed to install {pkg}.")
    
    print("Snap packages were successfully installed.")

    return True


def install_brave_browser() -> bool:
    """Installs Brave Browser.

    Installation instructions from <https://brave.com/linux/#linux>.
    """

    cmd = ("curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg "
    "https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg"
           )

    print("Getting Brave Browser's signing keys...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Brave Browser's fingerprint.")
    print("Successfully added Brave Browser's signing keys.")

    cmd = ("echo "
           "\"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] "
           "https://brave-browser-apt-release.s3.brave.com/ stable main\""
           " | "
           "tee /etc/apt/sources.list.d/brave-browser-release.list"
          )

    print("Adding Brave Browser's Apt repository...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Brave Browser's ppa.")
    print("Successfully added Brave Browser's Apt repository.")

    cmd = "apt update -y && apt install -y brave-browser"

    print("Installing Brave Browser's apt package...")
    _, errs_ = comm(cmd)
    if errs_:
        errs = capture_and_remove_apt_warning(errs_)
        if errs:
            raise InstallationError("Failed to install Brave Browser's apt package.")
    print("Installation successful.")
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

    print("Adding Docker signing keys...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Docker's fingerprint.")
    print("Successfully added signing keys.")


    cmd = ("echo "
           "\"deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] "
           "https://download.docker.com/linux/ubuntu "
           "$(lsb_release -cs) stable\""
           " | "
           "tee /etc/apt/sources.list.d/docker.list > /dev/null"
           )

    print("Adding Docker apt repository...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Docker's ppa.")
    print("Apt repository successfully added.")

    cmd = "apt update -y && apt install docker-ce docker-ce-cli containerd.io"
    print("Installing all necessary apt packages...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install Docker apt packages.")
    print("Installation successful.")

    # post-install step required for all Linux distros

    cmd = "groupadd docker && usermod -aG docker $USER"
    print("Adding Docker group and adding user to it...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Docker's group and/or add user to Docker's group.")
    print("Successfully added user to Docker group")

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
    print("Saving Fish shell's ppa...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to create Fish's ppa file.")
    print("Save successful.")

    fingerprint = "59FDA1CE1B84B3FAD89366C027557F056DC33CA5"
    cmd = f"apt-key adv --keyserver keyserver.ubuntu.com --recv-keys {fingerprint}"
    print("Adding Fish shell's fingerprint...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to add Fish's fingerprint.")
    print("Fingerprint successfully added.")

    cmd = "apt update -y && install -y fish"
    print("Installing Fish shell's apt package...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install Fish shell.")
    print("Installation successful.")

    return True


def install_google_chrome() -> bool:
    """Installs Google Chrome."""

    file_name = "google-chrome-stable_current_amd64.deb"
    file_url = f"https://dl.google.com/linux/direct/{file_name}"
    cmd = f"cd {DOWNLOADS_PATH} && curl -O {file_url}"

    print("Downloading Google Chrome's .deb file...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to download Google Chrome's .deb file.")
    print("Download successful.")

    cmd = "apt install -y ./{file_name}"
    print("Installing Google Chrome from .deb file...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to install Google Chrome from .deb file.")
    print("Installation successful.")

    return True


def install_neovim() -> bool:
    """Installs Neovim.

    Installation instructions form <>"
    """

    url = "https://github.com/neovim/neovim/releases/latest/download/nvim.appimage"
    cmd = f"cd {DOWNLOADS_PATH} && curl -LO {url}"
    print("Downloading Neovim's .appimage file...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to retrieve neovim .appimage file.")
    print("Download successful.")

    cmd = f"cd {DOWNLOADS_PATH} && -u $USER chmod u+x nvim.appimage"
    print("Making Neovim's .appimage executable...")
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to make nvim.appimage executable.")
    print("Chmod successful.")

    return True

def install_poetry() -> bool:
    """Installs Poetry (package manager for Python).

    Installation instructions from <https://python-poetry.org/docs/>.
    """

    python_v = ""
    if which("python3"):
        python_v = "3"
    cmd = f"curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python{python_v} -"
    print("Executing Poetry's installation script...")
    _, errs = comm(cmd)
    if errs:
        InstallationError("Poetry was not installed.")
    print("Execution successful.")

    return True

def install_not_ppkd_prog() -> bool:
    """Installs all programs not in apt nor snap packages."""

    # brave browser
    print("Installing Brave Browser...")
    try:
        install_brave_browser()
    except (InstallationError, TimeoutExpired):
        raise InstallationError("Brave browser was not installed")
    else:
        print("Successfully installed Brave Browser.")

    # docker
    print("Installing Docker...")
    try:
        install_docker()
    except (InstallationError, TimeoutExpired):
        raise InstallationError("Docker was not installed.")
    else:
        print("Successfully installed Docker.")


    # fish shell
    print("Installing Fish shell...")
    try:
        install_fish_shell()
    except (InstallationError, TimeoutExpired):
        raise InstallationError("Fish shell was not installed.")
    print("Successfully installed Fish shell.")

    # google chrome
    print("Installing Google Chrome...")
    try:
        install_google_chrome()
    except (InstallationError, TimeoutExpired):
        raise InstallationError("Google Chrome was not installed.")
    print("Successfully installed Google Chrome.")

    # neovim
    print("Installing Neovim...")
    try:
        install_neovim()
    except (InstallationError, TimeoutExpired):
        raise InstallationError("Neovim was not installed.")
    print("Successfully installed Neovim.")

    # poetry
    print("Installing Poetry...")
    try:
        install_poetry()
    except (InstallationError, TimeoutExpired):
        raise InstallationError("Poetry was not installed.")
    print("Successfully installed Poetry.")

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
    src = f"{DOWNLOADS_PATH}/{file}"
    dest = f"/usr/local/bin/{file}"

    try:
        copyfile(src, dest)
    except SameFileError:
        raise SameFileError("The source and destination files are the same.")

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
        raise SameFileError("The source and destination files are the same.")

    return True


def post_tmux() -> bool:
    """Fetches Tmux Plugin Manager and copies `.tmux.conf` file to `HOME_PATH`."""

    tpm_repo = "https://github.com/tmux-plugins/tpm"        # tpm repo url
    tpm_clone_path = "~/.tmux/plugins/tpm"                  # tpm repo dest path

    # clone Tmux Plugin Manager github repo
    cmd = f"git clone {tpm_repo} {tpm_clone_path}"
    _, errs = comm(cmd)
    if errs:
        raise InstallationError("Failed to clone Tmux Plugin Manager's github repo.")

    # copy .tmux.conf file
    src = f"{CONFIG_FILES_PATH}/tmux.conf"                  # tmux.conf source path
    dest = "~/.tmux.conf"                                   # tmux.conf dest path
    try:
        copyfile(src, dest)
    except SameFileError:
        raise SameFileError("The source and destination files are the same.") from SameFileError

    return True


def post_install() -> bool:
    """Procedures that should occur after all programs have been installed."""

    print("Starting post-installation procedures for Fish shell.")
    try:
        post_fish_shell()
    except InstallationError:
        raise InstallationError("Fish shell's post installation procedures failed.")

    print("Starting post-installation procedures for Neovim.")
    try:
        post_neovim()
    except InstallationError:
        raise InstallationError("Neovim's post installation procedures failed.")

    print("Starting post-installation procedures for Tmux.")
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
#if __name__ == "__main__":
#
#    pre_install()
#    install_apt_pkgs()
#    install_snap_pkgs()
#    install_not_ppkd_prog()
#    post_install()
#    cleanup()
