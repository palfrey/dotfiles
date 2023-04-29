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
      fixinterpreter = writeShellScriptBin "fixinterpreter"
        ''
          ${pkgs.patchelf}/bin/patchelf \
              --set-interpreter ${pkgs.glibc}/lib/ld-linux-x86-64.so.2 $1
        '';

      polybar-pulseaudio-control = callPackage ./pulseaudio-control.nix { };
      diff-highlight = callPackage ./diff-highlight.nix { };
      cargo-why = callPackage ./cargo-why.nix { };
      my-python-packages = p: with p; [
        pip
        virtualenvwrapper
      ];
      extraNodePackages = import ./node/override.nix { };
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
      signal-desktop
      flameshot
      just
      clang
      diff-highlight
      circleci-cli
      docker-compose
      yarn
      nodejs
      fixinterpreter
      awscli2
      terraform
      ripgrep
      fd
      arandr
      gnumake
      zip
      amazon-ecr-credential-helper
      meld
      pkgsUnstable.nix-init
      cargo-why
      extraNodePackages.nx
      nodePackages.pnpm
      unzip
      nix-index
      delta
      dbeaver
    ];
  };

  home.sessionVariables = {
    EDITOR = "vim";
    TERM = "xterm";
  };

  programs.zsh = {
    enable = true;
    initExtra = "unsetopt nomatch";
    dotDir = ".config/zsh";
    plugins = [{
      name = "zsh-nix-shell";
      file = "nix-shell.plugin.zsh";
      src = pkgs.fetchFromGitHub {
        owner = "chisui";
        repo = "zsh-nix-shell";
        rev = "v0.5.0";
        sha256 = "0za4aiwwrlawnia4f29msk822rj9bgcygw6a8a6iikiwzjjz0g91";
      };
    }];
    oh-my-zsh = {
      enable = true;
      plugins = [ "git" "kubectl" "pyenv" "command-not-found" "direnv" ];
      theme = "agnoster";
    };
  };

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;

}
