# Nix Development Shell

I am a nix user and this is the way I wind up using nix with python.
It is a simple shim that just gets UV to work with nix (and nixos), otherwise it works as expected.
UV has a lock and manages the python dependencies, while nix provides non-python binaries including my pre-commit.
This allows greater portability and does not require users to have nix.

## Direnv

Direnv (with nix-direnv) is how I activate the environment, here is the `.envrc` I use:

```
watch_file nix/shell.nix
use flake
layout python3
# This needs to be set after activating the environment to properly point at it
export UV_PROJECT_ENVIRONMENT="$VIRTUAL_ENV"
```
