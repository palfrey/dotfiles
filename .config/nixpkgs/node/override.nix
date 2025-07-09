{ pkgs
, system
}:

let nodePackages = import ./default.nix { inherit pkgs system; };
in nodePackages // {
  nx = nodePackages.nx.override {
    buildInputs = with pkgs; [
      pkgs.nodePackages.node-gyp-build
    ];
  };
}
