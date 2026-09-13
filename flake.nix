{
  description = "PyQt6 multimedia development shell";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };

      python = pkgs.python313.withPackages (ps: [
        ps.pyqt6
      ]);
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [
          python
          pkgs.qt6.qtmultimedia
          pkgs.pipewire
          pkgs.wireplumber
          pkgs.ffmpeg
          pkgs.python3Packages.mutagen
        ];

        shellHook = ''
          export QT_PLUGIN_PATH="${pkgs.qt6.qtmultimedia}/lib/qt-6/plugins"
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [
            pkgs.pipewire
            pkgs.ffmpeg
          ]}:$LD_LIBRARY_PATH"
        '';
      };
    };
}
