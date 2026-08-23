{ pkgs, ... }:
{
  home = {
    username = "runic";
    homeDirectory = "/home/runic";
    packages = [
      pkgs.kubectl
      pkgs.k9s
      pkgs.kubernetes-helm
      pkgs.kubectx
    ];
  };
  home.stateVersion = "26.05";
}
