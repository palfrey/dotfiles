{ lib
, fetchPypi
, python3
}:

python3.pkgs.buildPythonPackage rec {
  pname = "ppretty";
  version = "1.3";
  pyproject = true;

  src = fetchPypi {
    inherit pname version;
    hash = "sha256-pfvhe5rp77mo12Qj2Ex8WvcTCwjmw7KAeOwlwkT4g+U=";
    extension = "zip";
  };

  build-system = with python3.pkgs; [
    setuptools
    wheel
  ];

  pythonImportsCheck = [
    "ppretty"
  ];

  meta = {
    description = "Convert python objects to a human readable format";
    homepage = "https://pypi.org/project/ppretty/";
    license = lib.licenses.bsd3;
    maintainers = with lib.maintainers; [ ];
  };
}
