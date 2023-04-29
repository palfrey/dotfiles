nix-env -f '<nixpkgs>' -iA nodePackages.node2nix
node2nix -i node-packages.json
nix-env -f default.nix -iA nx
