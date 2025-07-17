{ lib
, fetchFromGitHub
, python3
, pkgs
}:

python3.pkgs.buildPythonPackage rec {
  pname = "randrctl";
  version = "1.10.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "koiuo";
    repo = "randrctl";
    rev = version;
    hash = "sha256-YJd8cQQo0RIYyRzOGqKBcQYLshXXRh5f2aor9qDoIE4=";
  };

  build-system = with python3.pkgs; [
    setuptools
    wheel
  ];

  pythonRelaxDeps = true;

  dependencies = with python3.pkgs; [
    argcomplete
    pyyaml
    pbr
    pkgs.xorg.xrandr
  ];

  preConfigure = ''
    export PBR_VERSION=${version}
  '';

  postPatch = ''
    substituteInPlace randrctl/xrandr.py \
        --replace-fail 'EXECUTABLE = "/usr/bin/xrandr"' 'EXECUTABLE = "${pkgs.xorg.xrandr}/bin/xrandr"'
  '';

  pythonImportsCheck = [
    "randrctl"
  ];

  meta = {
    description = "Profile based screen manager for X";
    homepage = "https://github.com/koiuo/randrctl";
    changelog = "https://github.com/koiuo/randrctl/blob/${src.rev}/CHANGELOG.md";
    license = lib.licenses.gpl3Only;
    maintainers = with lib.maintainers; [ ];
  };
}
