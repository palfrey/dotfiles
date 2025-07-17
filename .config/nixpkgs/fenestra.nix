{ lib
, python3
, fetchFromGitHub
, callPackage
, pkgs
}:

let
  randrctl = callPackage ./randrctl.nix { };
  ppretty = callPackage ./ppretty.nix { };
  dormer = pkgs.callPackage ./dormer.nix { };
  pulseaudio-control = callPackage ./pulseaudio-control.nix { };
  polybar-i3-windows = callPackage ./polybar-i3-windows.nix { };
in
python3.pkgs.buildPythonApplication rec {
  pname = "fenestra";
  version = "unstable-2025-07-09";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "palfrey";
    repo = "fenestra";
    rev = "966d926";
    hash = "sha256-CbnpTX1lIlgUvZt2v/3zLScDOD+CZNMP1Un+SnoWQ7I=";
    fetchSubmodules = true;
  };

  build-system = with python3.pkgs; [
    setuptools
    wheel
  ];

  nativeBuildInputs = [
    pkgs.wrapGAppsHook
    pkgs.gobject-introspection
    python3.pkgs.pygobject3
  ];

  preFixup = ''
    makeWrapperArgs+=("''${gappsWrapperArgs[@]}")
  '';

  postPatch = ''
    substituteInPlace fenestra/polybar/pulseaudio-control.ini \
        --replace-fail '~/.config/polybar/polybar-pulseaudio-control/pulseaudio-control.bash' '${pulseaudio-control}/bin/pulseaudio-control'
    substituteInPlace fenestra/polybar/i3-windows.ini.jinja \
        --replace-fail '{{ script_folder }}/polybar/polybar-i3-windows/module.py' '${polybar-i3-windows}/bin/polybar-i3-windows'
  '';

  buildInputs = [
    pkgs.glib
  ];

  dependencies = with python3.pkgs; [
    jinja2
    ewmh
    xcffib
    randrctl
    pyudev
    ppretty
    pydbus
    pkgs.xorg.xrandr
    dormer
    i3ipc
    polybar-i3-windows
  ];

  pythonImportsCheck = [
    "fenestra"
  ];

  meta = {
    description = "Tooling for setting up various desktop config";
    homepage = "https://github.com/palfrey/fenestra";
    license = lib.licenses.agpl3Only;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "fenestra";
  };
}
