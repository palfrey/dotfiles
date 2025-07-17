{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    nix-unstable.url = "github:nixos/nixpkgs/master";
    nixos-hardware.url = "github:NixOS/nixos-hardware/master";
    home-manager = {
      url = "github:nix-community/home-manager/release-25.05";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };
  outputs = { self, nixpkgs, nixos-hardware, home-manager, nix-unstable }: {
    nixosConfigurations.cage = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        ./cage-configuration.nix
        nixos-hardware.nixosModules.framework-amd-ai-300-series

        home-manager.nixosModules.home-manager
        {
          home-manager.useGlobalPkgs = true;
          home-manager.useUserPackages = true;
          home-manager.extraSpecialArgs = {
            pkgs-unstable = import nix-unstable {
              system = "x86_64-linux"; #  FIXME: inherit
              config.allowUnfree = true;
            };
          };
          home-manager.users.palfrey = import ../.config/nixpkgs/home.nix;
        }
      ];
    };
  };
}
