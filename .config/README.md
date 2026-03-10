These are some development configs I have for various tools.

They're only active if you use the nix devshell or otherwise install lefthook.


## Suggested `.envrc`

Here is the file I use:

```
watch_file nix/shell.nix
use flake
layout python3
export UV_PROJECT_ENVIRONMENT="$VIRTUAL_ENV"
uv sync --all-groups
```