#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import pathlib
from exceptions import InstallationError, ImgDownloadError
from imgs import download_all_imgs
from installers import (
    cleanup,
    install_apt_pkgs,
    install_not_ppkd_prog,
    install_snap_pkgs,
    pre_install,
)
from post_installers import post_install


def is_user_root() -> bool:
    """Checks if the user executing the script is root."""

    exec_path = pathlib.Path.home()
    
    if "root" in str(exec_path):
        return True
    return False


def main_installation() -> None:
    """Installs all software to an Ubuntu machine."""

    print("Installing packages... This might take a few minutes.")

    print("Starting pre-installation procedures.")
    try:
        pre_install()
    except InstallationError:
        print("Pre-installation procedures failed.")
        print("Exiting...")
        return None

    print("Pre-installation procedures were succesful.")

    print("Continuing with software installation...")
    try:
        install_apt_pkgs()
    except InstallationError:
        print("There was a problem installing apt packages.")
        print("Exiting...")
        return None

    try:
        install_snap_pkgs()
    except InstallationError:
        print("There was a problem installing snap packages.")
        print("Exiting...")
        return None

    try:
        install_not_ppkd_prog()
    except InstallationError:
        print("There was a problem installing other packages.")
        print("Exiting...")
        return None

    print("Installation successful.")
    
    print("Execute this script again as not root for post-installation procedures and cleanup")


def main_post_installation() -> None:
    """Executes post-installation procedures."""

    print("Starting post-installation procedures.")
    try:
        post_install()
    except InstallationError:
        print("Post-installation procedures failed.")
        print("Exiting...")
        return None
    print("Post-installation procedures were successful.")
    
    print("Starting to download all images.")
    try:
        download_all_imgs()
    except ImgDownloadError:
        print("Some images failed to download.")
        print("Continuing...")


def main_cleanup() -> None:
    """Executes cleanup procedures."""

    print("Cleaning up the mess.")
    if not cleanup():
        print("Failed cleanup procedures. You could still and should perform this manually.")
        print("Delete downloads directory.")
    else:
        print("Cleanup successful.")



def main():
    """Entry point for Apollo installer."""

    if is_user_root():
        main_installation()
    else:
        main_post_installation()
        main_cleanup()

    print("All done here.")


if __name__ == "__main__":

    main()
