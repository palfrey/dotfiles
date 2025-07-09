{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    nixos-hardware.url = "github:NixOS/nixos-hardware/master";
  };
  outputs = { self, nixpkgs, nixos-hardware }: {
    nixosConfigurations.cage = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./cage-configuration.nix
        nixos-hardware.nixosModules.framework-amd-ai-300-series
        ];
    };
  };
}
