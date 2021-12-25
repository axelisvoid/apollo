import os.path
from cli import comm
from exceptions import CliError, ImgDownloadError, UnexistentPathError


PROF_PIC_URL = "https://avatars.githubusercontent.com/u/66369315?v=4"
WALLPPER_URL = "https://user-images.githubusercontent.com/66369315/146630739-dc8ee9ed-8c68-41bf-bed2-3f6f35ac804e.png"
CODE_BGD_URL = "https://user-images.githubusercontent.com/66369315/146630747-d528c3e2-eafe-4aa9-b1db-59572cac4567.png"
PICS_DEST_PARENT = "Pictures/desk_custom"


def download_img(url: str, dest: str, output: str) -> bool:
    """Retreives an image from `url` and saves it in the `dest` directory with `output`."""

    # dest is relative to `~/` directory
    if not os.path.exists(dest):
        raise UnexistentPathError(f"Path {dest} does not exists.")

    cmd = f"curl -o ~/{dest}/{output} {url}"
    _, errs = comm(cmd)

    if errs:
        raise ImgDownloadError(f"Could not fetch image from {url}")
    return True


def download_profile_pic() -> bool:
    """Fetches profile picture."""

    output = "profilepic_jpeg"
    return download_img(PROF_PIC_URL, PICS_DEST_PARENT, output)


def download_wallpaper() -> bool:
    """Fetches desktop wallpaper."""

    output = "wallpaper.png"
    return download_img(WALLPPER_URL, PICS_DEST_PARENT, output)


def download_code_bgd() -> bool:
    """Fetches code background."""

    output = "code_bgd.png"
    return download_img(CODE_BGD_URL, PICS_DEST_PARENT, output)


def download_all_imgs() -> None:
    """Fetches all images used to customize desktop."""

    cmd = f"mkdir {PICS_DEST_PARENT}"
    _, errs = comm(cmd)
    if errs:
        raise CliError(f"Could not create {PICS_DEST_PARENT}")

    try:
        download_profile_pic()
    except ImgDownloadError:
        raise ImgDownloadError("Failed to download profile picture.")

    try:
        download_wallpaper()
    except ImgDownloadError:
        raise ImgDownloadError("Failed to download wallpaper picture.")

    try:
        download_code_bgd()
    except ImgDownloadError:
        raise ImgDownloadError("Failed to download code background picture.")

