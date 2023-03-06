{ config, pkgs, ... }:

{
  imports =
    [
      # Include the results of the hardware scan.
      ./hardware-configuration.nix
      ./cachix.nix
      /home/palfrey/src/nixos-hardware/dell/xps/15-9520/nvidia/default.nix
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;
  boot.loader.efi.efiSysMountPoint = "/boot/efi";

  # Setup keyfile
  boot.initrd.secrets = {
    "/crypto_keyfile.bin" = null;
  };

  # Enable swap on luks
  boot.initrd.luks.devices."luks-73da88a7-d71c-457d-ad1c-f35cf857a5ae".device = "/dev/disk/by-uuid/73da88a7-d71c-457d-ad1c-f35cf857a5ae";
  boot.initrd.luks.devices."luks-73da88a7-d71c-457d-ad1c-f35cf857a5ae".keyFile = "/crypto_keyfile.bin";

  networking.hostName = "strath"; # Define your hostname.

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "Europe/London";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_GB.UTF-8";

  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_GB.UTF-8";
    LC_IDENTIFICATION = "en_GB.UTF-8";
    LC_MEASUREMENT = "en_GB.UTF-8";
    LC_MONETARY = "en_GB.UTF-8";
    LC_NAME = "en_GB.UTF-8";
    LC_NUMERIC = "en_GB.UTF-8";
    LC_PAPER = "en_GB.UTF-8";
    LC_TELEPHONE = "en_GB.UTF-8";
    LC_TIME = "en_GB.UTF-8";
  };

  # Configure keymap in X11
  services.xserver = {
    layout = "gb";
    xkbVariant = "mac";
  };

  # Configure console keymap
  console.keyMap = "uk";

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.palfrey = {
    isNormalUser = true;
    description = "Tom Parker-Shemilt";
    extraGroups = [ "networkmanager" "wheel" "audio" "docker" ];
  };

  environment.sessionVariables = {
    TERMINAL = "alacritty";
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;

  users.defaultUserShell = pkgs.zsh;
  hardware.bluetooth.enable = true;
  sound.enable = true;
  hardware.pulseaudio = {
    enable = true;
    package = pkgs.pulseaudioFull;
  };
  nixpkgs.config.pulseaudio = true;
  services.blueman.enable = true;
  services.udisks2.enable = true;
  xdg.mime.enable = true;
  virtualisation.docker.enable = true;

  programs.zsh = {
    enable = true;
  };

  nix = {
    package = pkgs.nixFlakes;
    extraOptions = ''
      experimental-features = nix-command flakes
    '';
  };

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs;
    let
      polybar = pkgs.polybar.override {
        i3Support = true;
        iwSupport = true;
        pulseSupport = true;
        nlSupport = true;
      };
    in
    [
      vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
      wget
      curl
      lshw
      pciutils
      firefox
      git
      _1password-gui
      slack
      discord
      alacritty
      python3
      python2
      polybar
      jq
      file
      dropbox
      htop
      (import (fetchTarball https://github.com/cachix/devenv/archive/v0.6.tar.gz)).default
      psmisc
      powertop
    ];

  fonts.fonts = with pkgs; [
    noto-fonts
    noto-fonts-cjk
    noto-fonts-emoji
    liberation_ttf
    fira-code
    fira-code-symbols
    mplus-outline-fonts.githubRelease
    dina-font
    proggyfonts
    powerline-fonts
    unifont
    siji
  ];


  networking.firewall = {
    allowedTCPPorts = [ 17500 ];
    allowedUDPPorts = [ 17500 ];
  };

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # };

  # List services that you want to enable:

  services.hardware.bolt.enable = true;

  services.xserver = {
    enable = true;
    desktopManager.xterm.enable = false;
    displayManager = {
      defaultSession = "none+i3";
    };
    windowManager.i3 = {
      enable = true;
      extraPackages = with pkgs; [
        i3lock #default i3 screen locker
      ];
    };
    videoDrivers = [ "nvidia" ];
  };
  hardware.nvidia.package = config.boot.kernelPackages.nvidiaPackages.stable;
  boot.kernelPackages = pkgs.linuxPackages_latest;
  #hardware.nvidia.modesetting.enable = true;
  hardware.nvidia.prime = {
    offload.enable = true;
  };

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "22.11"; # Did you read the comment?

}
