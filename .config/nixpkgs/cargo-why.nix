{ lib, stdenv, rustPlatform, fetchFromGitHub, pkg-config, openssl }:

rustPlatform.buildRustPackage rec {
  pname = "cargo-why";
  version = "0.2.0";

  src = fetchFromGitHub {
    owner = "boringcactus";
    repo = pname;
    rev = "9929b2077bcf832bb046261337b21e234167a21f";
    sha256 = "sha256-Jp4kQFAuCa4SiPz2h8EO/ZQwi5VNj1EiZ6mm/NK2LFM=";
  };

  cargoHash = "sha256-YE8UZ8b6/DfQH74AIYmHtxSS5/amujGP/sGILqgPPcQ=";

  nativeBuildInputs = [ ];

  buildInputs = [ ];

  meta = with lib; {
    description = "Traces dependency paths to show why a crate was required";
    homepage = "https://github.com/boringcactus/cargo-why";
    license = licenses.mit;
    maintainers = with maintainers; [ "Melody Horn" ];
  };
}

  