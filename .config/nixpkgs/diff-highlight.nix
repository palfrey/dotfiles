{ stdenv, pkgs }:

let
  version = "0.0.1";
in
stdenv.mkDerivation {
  pname = "diff-highlight";
  inherit version;
  src = ../../bin/diff-highlight;

  buildInputs = [
    pkgs.perl
  ];

  unpackPhase = ''
    for srcFile in $src; do
      cp $srcFile $(stripHash $srcFile)
    done
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp diff-highlight $out/bin/diff-highlight
  '';
}
