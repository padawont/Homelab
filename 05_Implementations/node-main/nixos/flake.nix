{
  description = "NixOS configurations for the homelab (node-main)";
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    disko.url = "github:nix-community/disko";
    disko.inputs.nixpkgs.follows = "nixpkgs";
    home-manager.url = "github:nix-community/home-manager/release-26.05";
    home-manager.inputs.nixpkgs.follows = "nixpkgs";
    deploy-rs.url = "github:serokell/deploy-rs";
    deploy-rs.inputs.nixpkgs.follows = "nixpkgs";
    sops-nix.url = "github:Mic92/sops-nix";
    sops-nix.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    {
      self,
      nixpkgs,
      disko,
      home-manager,
      deploy-rs,
      sops-nix,
      ...
    }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in
    {
      nixosConfigurations.node-main = nixpkgs.lib.nixosSystem {
        inherit system;
        modules = [
          disko.nixosModules.disko
          sops-nix.nixosModules.sops
          home-manager.nixosModules.home-manager
          ./disk-config.nix
          ./configuration.nix
        ] ++ (nixpkgs.lib.optional (builtins.pathExists ./hardware-configuration.nix) ./hardware-configuration.nix);
      };

      deploy.nodes.node-main = {
        hostname = "192.168.111.7";
        sshUser = "root";
        profiles.system = {
          user = "root";
          path = deploy-rs.lib.${system}.activate.nixos self.nixosConfigurations.node-main;
        };
        autoRollback = true;
        magicRollback = true;
        confirmTimeout = 60;
      };

      checks = builtins.mapAttrs (sys: deployLib: deployLib.deployChecks self.deploy) deploy-rs.lib;
    };
}
