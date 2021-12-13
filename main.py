#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from installers import install_apt_pkgs, install_snap_pkgs, install_not_ppkd_prog
# TODO: Add cleanup and post_install function imports


def main():
    """Entry point for Apollo installer."""

    print("Installing packages... This might take a few minutes.")

    error = 0
    while error == 0:
        try:
            install_apt_pkgs()
        except InstallationError:
            print("There was a problem installing apt packages.")
            error += 1
        try:
            install_snap_pkgs()
        except InstallationError:
            print("There was a problem installing snap packages.")
            print("Exiting...")
            error += 1
        try:
            install_not_ppkd_prog()
        except InstallationError:
            print("There was a problem installing other packages.")
            print("Exiting...")
            error += 1

    if error != 0:
        print("Installation process was interrupted. Exiting...")
        break

#    print("Installation successful.")
#
#    print("Continuing to post-installation phase.")
#    post_install()
#    print("Post-installation phase successful.")
#
#    print("Cleaning up downloaded files.")
#    cleanup()
#
#    print("Cleanup successful.")
#
#    print("All done here.")


if __name__ == "__main__":

    main()
