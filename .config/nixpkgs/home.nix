{ config, pkgs, ... }:

{
  home = {
    username = "palfrey";
    homeDirectory = "/home/palfrey";
    stateVersion = "25.05";
    packages = with pkgs; let
      quodlibet = pkgs.quodlibet.override {
        withDbusPython = true;
        withPypresence = true;
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
      # extraNodePackages = import ./node/override.nix { inherit pkgs system; };
    in
    [
      vscode
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
      zoom-us
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
      nix-init
      # cargo-why
      # extraNodePackages.nx
      nodePackages.pnpm
      unzip
      nix-index
      delta
      dbeaver-bin
    ];
  };

  home.sessionVariables = {
    EDITOR = "vim";
    TERM = "xterm";
  };

  programs.zsh = {
    enable = true;
    initContent = "unsetopt nomatch";
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
      plugins = [ "git" "kubectl" "command-not-found" "direnv" ];
      theme = "agnoster";
    };
  };

  # Let Home Manager install and manage itself.
  programs.home-manager.enable = true;
}
