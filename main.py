#!/usr/bin/env python3
# -*- coding: utf-8 -*-


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


def main():
    """Entry point for Apollo installer."""

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

    # post-installation

    print("Starting post-installation procedures.")
    try:
        post_install()
    except InstallationError:
        print("Post-installation procedures failed.")
        print("Exiting...")
        return None
    print("Post-installation procedures were successful.")

    # images
    
    print("Starting to download all images.")
    try:
        download_all_imgs()
    except ImgDownloadError:
        print("Some images failed to download.")
        print("Continuing...")

    # cleanup

    print("Cleaning up the mess.")
    if not cleanup():
        print("Failed cleanup procedures. You could still and should perform this manually.")
        print("Delete downloads directory.")
    else:
        print("Cleanup successful.")

    print("All done here.")


if __name__ == "__main__":

    main()
