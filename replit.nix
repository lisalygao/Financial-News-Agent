{ pkgs }: {
  deps = [
    pkgs.google-cloud-sdk-gce
    pkgs.replitPackages.prybar-python310
    pkgs.replitPackages.stderred
  ];
}