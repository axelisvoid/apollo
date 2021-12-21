from shutil import copyfile, SameFileError
from cli import comm
from exceptions import InstallationError
from installers import CONFIG_FILES_PATH, DOWNLOADS_PATH, HOME_PATH


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

