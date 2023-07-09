{
  description = "Thanatosns dev shell";
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system};
      in {
        devShells.default =
          let myPythonPackages = ps: with ps; [ docformatter ];
          in pkgs.mkShell {
            packages = with pkgs; [
              pdm
              pyright
              black
              isort
              (python3.withPackages myPythonPackages)
              exiftool
            ];
          };
      });
}
