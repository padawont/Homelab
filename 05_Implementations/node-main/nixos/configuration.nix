{ lib, pkgs, ... }:
{
  # EFI boot (machine is UEFI)
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "node-main";
  # DHCP handled by hardware-configuration.nix (generated at install)
  networking.extraHosts = ''
    192.168.111.7 rancher.local
  '';

  system.stateVersion = "26.05";

  environment.systemPackages = with pkgs; [
    curl
    git
    vim
    htop
  ];

  services.openssh = {
    enable = true;
    settings = {
      PasswordAuthentication = false;
      PermitRootLogin = "prohibit-password";
    };
  };

  users.users.root = {
    hashedPassword = "$6$KkEgvWAlficL58pf$AHzYybdY3xmiYgglFl71zWdfGv80kuuJBMoYujD0pY9NIBoZDJ8JkQGfTJ2pQ05PCdqt6zAbiNwTKNK.mgHyC/";
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILXGB6KihcZn5QI8875cbLTtb7ss3eBncfrqtvV4fm70 linuxrunic@homelab"
    ];
  };

  users.users.runic = {
    isNormalUser = true;
    extraGroups = [ "wheel" ];
    hashedPassword = "$6$KkEgvWAlficL58pf$AHzYybdY3xmiYgglFl71zWdfGv80kuuJBMoYujD0pY9NIBoZDJ8JkQGfTJ2pQ05PCdqt6zAbiNwTKNK.mgHyC/";
    openssh.authorizedKeys.keys = [
      "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILXGB6KihcZn5QI8875cbLTtb7ss3eBncfrqtvV4fm70 linuxrunic@homelab"
    ];
  };
  security.sudo.wheelNeedsPassword = false;

  home-manager = {
    useGlobalPkgs = true;
    users.runic = import ./home.nix;
  };

  services.k3s = {
    enable = true;
    role = "server";
    extraFlags = "--write-kubeconfig-mode 644";
    # data dir defaults to /var/lib/rancher/k3s -> on the sda data disk
  };

  networking.firewall = {
    allowedTCPPorts = [ 6443 10250 ];
    allowedUDPPorts = [ 8472 ];
  };

  sops.age.sshKeyPaths = [ "/etc/ssh/ssh_host_ed25519_key" ];
}
