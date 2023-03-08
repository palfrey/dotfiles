{ stdenv, fetchFromGitHub, pkgs }:

let
  version = "3.1.1";
in
stdenv.mkDerivation {
  pname = "polybar-pulseaudio-control";
  inherit version;
  src = fetchFromGitHub {
    owner = "marioortizmanero";
    repo = "polybar-pulseaudio-control";
    rev = "v3.1.1";
    sha256 = "sha256-egCBCnhnmHHKFeDkpaF9Upv/oZ0K3XGyutnp4slq9Vc=";
  };

  buildInputs = [
    pkgs.gnugrep
    pkgs.gnused
    pkgs.gawk
    pkgs.pulseaudio
    pkgs.coreutils-full
  ];

  buildPhase = ''
    substituteInPlace pulseaudio-control.bash \
    --replace grep ${pkgs.gnugrep}/bin/grep \
    --replace pactl ${pkgs.pulseaudio}/bin/pactl \
    --replace " sed" " ${pkgs.gnused}/bin/sed" \
    --replace awk ${pkgs.gawk}/bin/awk \
    --replace " tr" " ${pkgs.coreutils-full}/bin/tr" \
    --replace " cut" " ${pkgs.coreutils-full}/bin/cut" \
    --replace sort ${pkgs.coreutils-full}/bin/sort
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp pulseaudio-control.bash $out/bin/pulseaudio-control
  '';
}
