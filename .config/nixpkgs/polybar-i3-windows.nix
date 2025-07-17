{ lib
, python3
, fetchFromGitHub
,
}:

python3.pkgs.buildPythonApplication rec {
  pname = "polybar-i3-windows";
  version = "unstable-2024-07-01";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "palfrey";
    repo = "polybar-i3-windows";
    rev = "5b12e6a12602564475fc40d3057b872a238d02b1";
    hash = "sha256-/leJliCOvIlY8CXu3L0lBwJMALFNNtbW72V2hZ7e06M=";
  };

  build-system = with python3.pkgs; [
    setuptools
    wheel
  ];

  dependencies = with python3.pkgs; [
    i3ipc
  ];

  meta = {
    description = "";
    homepage = "https://github.com/palfrey/polybar-i3-windows";
    license = lib.licenses.mit;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "polybar-i3-windows";
    platforms = lib.platforms.all;
  };
}
