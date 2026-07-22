# Forgejo — NixOS Configuration
{ config, pkgs, ... }:

{
  networking.firewall.allowedTCPPorts = [ 3000 22 ];

  networking.extraHosts =
    ''
      192.168.111.10 git.homelab.internal
    '';
}
