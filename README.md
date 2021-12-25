# apollo script

Python script to add a few apps in a new installation of Ubuntu 20.04 LTS.

# list of apps installed

- Ubuntu apt packages
    * apt-transport-https
    * build-essential
    * cmake
    * curl
    * ca-certificates
    * gnupg
    * htop
    * lsb-release
    * mmv
    * neovim
    * python3-dev
    * pkg-config
    * tmux

- Snap packages
    * bitwarden
    * code (visual studio code)
    * libreoffice
    * signal-desktop
    * spotify
    * sublime-text
    * vlc

- Other
    * brave browser
    * docker engine and docker compose v2
    * fish shell
    * google chrome
    * poetry (python's package manager)

## Steps to take after installation process
1. Change default shell to Fish shell by entering ``chsh -s ` which fish` ``