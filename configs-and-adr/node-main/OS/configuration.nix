{ config, pkgs, ... }:

{
  imports = [ ./hardware-configuration.nix ];

  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "nixos";
  networking.useDHCP = true;

  services.openssh.enable = true;
  services.openssh.settings.PasswordAuthentication = true;
  services.openssh.settings.PermitRootLogin = "no";

  services.openiscsi.enable = true;
  services.openiscsi.name = "iqn.2026-07.local.nixos:initiator";

  virtualisation.docker.enable = true;

  services.k3s = {
    enable = true;
    role = "server";
    extraFlags = [
      "--disable=servicelb"
    ];
    disable = [
      "traefik"
    ];
  };

  users.users.nixos = {
    isNormalUser = true;
    password = "nixos";
    extraGroups = [ "wheel" "docker" ];
  };

  security.sudo.wheelNeedsPassword = false;

  networking.firewall.enable = true;
  networking.firewall.allowedTCPPorts = [ 22 80 443 6443 ];
  networking.firewall.allowedUDPPorts = [ 8472 ];
  networking.firewall.allowPing = true;

  boot.kernelModules = [ "iscsi_tcp" ];

  environment.systemPackages = with pkgs; [
    btop
    kubectl
    kubernetes-helm
    k3s
    openiscsi
    nfs-utils
    cryptsetup
    k9s
    curl
    git
    vim
  ];

  fileSystems."/var/lib/longhorn" = {
    device = "/dev/disk/by-label/longhorn";
    fsType = "ext4";
  };

  systemd.tmpfiles.settings = {
    "10-iscsiadm" = {
      "/usr/bin/iscsiadm" = {
        "L+" = {
          argument = "/run/current-system/sw/bin/iscsiadm";
          mode = "0755";
          group = "root";
          user = "root";
        };
      };
    };
  };

  system.stateVersion = "26.05";
}
