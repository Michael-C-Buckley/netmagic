{pkgs ? import <nixpkgs> {}}:
pkgs.mkShellNoCC {
  buildInputs = with pkgs; [
    # Nix
    alejandra

    # Python
    python313
    uv
    ty
    ruff
    gcc
    pkg-config

    # Pre-commit
    lefthook
    typos
    bandit
  ];
  env = {
    LD_LIBRARY_PATH = with pkgs;
      lib.makeLibraryPath [
        stdenv.cc.cc
      ];
  };

  shellHook = ''
    lefthook install
    export LOCALE_ARCHIVE="${pkgs.glibcLocales}/lib/locale/locale-archive"
    export LC_ALL="C.UTF-8"
    export UV_LINK_MODE=copy
    export UV_PROJECT_ENVIRONMENT="$VIRTUAL_ENV"
    git status --short --branch
  '';
}

