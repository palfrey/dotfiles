{ config, pkgs, ... }:

{
  home = {
    username = "palfrey";
    homeDirectory = "/home/palfrey";
    stateVersion = "22.11";
    packages = with pkgs; let
      pkgsUnstable = import <nixpkgs-unstable> { config = { allowUnfree = true; }; };
      quodlibet = pkgs.quodlibet.override {
        withDbusPython = true;
        withPypresence = true;
        withPyInotify = true;
        withMusicBrainzNgs = true;
      };
      polybar-pulseaudio-control = callPackage ./pulseaudio-control.nix { };
      my-python-packages = p: with p; [
        pip
      ];
    in
    [
      pkgsUnstable.vscode
      pavucontrol
      rustup
      feh
      udiskie
      redshift
      rofi
      quodlibet
      direnv
      playerctl
      beets
      (pkgs.python3.withPackages my-python-packages)
      pkgsUnstable.zoom-us
      dunst
      polybar-pulseaudio-control
    ];
  };

  home.sessionVariables = {
    EDITOR = "vim";
    TERM = "xterm";
  };

  programs.zsh = {
    enable = true;
    initExtra = "unsetopt nomatch";
    oh-my-zsh = {
      enable = true;
      plugins = [ "git" "kubectl" "pyenv" "command-not-found" "direnv" ];
      theme = "agnoster";
    };
  };

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;

}
