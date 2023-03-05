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
      polybar-pulseaudio-control = stdenv.mkDerivation rec {
        pname = "polybar-pulseaudio-control";
        version = "3.1.1";
        src = fetchFromGitHub {
          owner = "marioortizmanero";
          repo = "polybar-pulseaudio-control";
          rev = "v3.1.1";
          sha256 = "sha256-egCBCnhnmHHKFeDkpaF9Upv/oZ0K3XGyutnp4slq9Vc=";
        };

        buildInputs = [
          pulseaudio
        ];

        installPhase = ''
          mkdir -p $out/bin
          cp pulseaudio-control.bash $out/bin/pulseaudio-control
        '';
      };
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
