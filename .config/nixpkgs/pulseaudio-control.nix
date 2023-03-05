{ stdenv, fetchFromGitHub, pulseaudio, gnugrep, gnused }:

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
    gnugrep
    gnused
    pulseaudio
  ];

  buildPhase = ''
    substituteInPlace pulseaudio-control.bash \
    --replace grep ${gnugrep}/bin/grep \
    --replace pactl ${pulseaudio}/bin/pactl \
    --replace sed ${gnused}/bin/sed
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp pulseaudio-control.bash $out/bin/pulseaudio-control
  '';
}
