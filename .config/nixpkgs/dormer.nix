{ lib
, python3
, fetchFromGitHub
,
}:

python3.pkgs.buildPythonApplication rec {
  pname = "dormer";
  version = "unstable-2025-07-09";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "palfrey";
    repo = "dormer";
    rev = "8443ad66192cc4bc034951dc2df48da720d6bd61";
    hash = "sha256-9ucSxHr3zoWCoZ62wylc2Ko1KGEhLOOxhv8n0Olq0Pc=";
  };

  build-system = [
    python3.pkgs.setuptools
    python3.pkgs.wheel
  ];

  dependencies = with python3.pkgs; [
    i3ipc
    pyyaml
    typing-extensions
  ];

  pythonImportsCheck = [
    "dormer"
  ];

  meta = {
    description = "Tool for saving/restoring i3 workspace->output mappings";
    homepage = "https://github.com/palfrey/dormer";
    license = lib.licenses.agpl3Only;
    maintainers = with lib.maintainers; [ ];
    mainProgram = "dormer";
  };
}
