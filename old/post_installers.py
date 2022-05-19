from pathlib import Path
from shutil import copyfile, SameFileError
from cli import comm, car_expected_err_msg
from exceptions import CliError, InstallationError
from installers import CONFIG_FILES_PATH


HOME_PATH = Path.home()


def post_fish_shell() -> bool:
    """Sets fish as the default shell and copies fish functions to their configuration directory."""

    config_dest = f"{HOME_PATH}/.config/fish/functions"

    cmd = f"mkdir -p {config_dest}"
    _, errs = comm(cmd)
    if errs:
        raise CliError(f"Failed to create {config_dest} directory.")

    files = ["fish_greeting.fish", "fish_prompt.fish"]
    for file in files:
        src = f"{CONFIG_FILES_PATH}/fish/{file}"
        try:
            copyfile(src, f"{config_dest}/{file}")
        except SameFileError:
            raise SameFileError("The source and destination files are the same.") from SameFileError

    return True


def post_neovim() -> None:
    """Copies neovim's config file to its repective directory."""

    dst = f"{HOME_PATH}/.config/neovim"
    cmd = f"mkdir -p {dst}"
    _, errs = comm(cmd)
    if errs:
        raise CliError(f"Failed to create {cmd} directory.")

    src = f"{CONFIG_FILES_PATH}/neovim/init.vim"
    try:
        copyfile(src, f"{dst}/init.vim")
    except SameFileError:
        raise SameFileError("The source and destination files are the same.") from SameFileError


def post_tmux() -> bool:
    """Fetches Tmux Plugin Manager and copies `.tmux.conf` file to `HOME_PATH`."""

    tpm_repo = "https://github.com/tmux-plugins/tpm"        # tpm repo url
    tpm_clone_path = f"{HOME_PATH}/.tmux/plugins/tpm"       # tpm repo dest path

    # clone Tmux Plugin Manager github repo
    cmd = f"git clone {tpm_repo} {tpm_clone_path}"
    _, errs_ = comm(cmd)
    if errs_:
        expected_err_msg = bytes(f"Cloning into '{HOME_PATH}/.tmux/plugins/tpm'...\n", "utf8")
        errs = car_expected_err_msg(expected_err_msg, errs_)
        if errs:
            raise InstallationError("Failed to clone Tmux Plugin Manager's github repo.")

    # copy .tmux.conf file
    src = f"{CONFIG_FILES_PATH}/tmux/tmux.conf"             # tmux.conf source path
    dest = f"{HOME_PATH}/.tmux.conf"                        # tmux.conf dest path
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
