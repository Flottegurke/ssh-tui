# ssh-tui
ssh-tui is a sleek and minimal terminal user interface (TUI) for managing SSH connections.

## Features
- Quickly filter through SSH connections
- Supports SSH keys and password authentication
- Manage SSH connections from within the TUI (add, edit, delete)
- Connections get stored in your `~/.ssh/config` file

## Requirements
- Python 3.11+
- [textual](https://github.com/Textualize/textual)
- [rich](https://github.com/Textualize/rich)
- A [functional `~/.ssh/config file`](https://gist.github.com/numberwhun/d986bb536af15c5fccdcd5dfa656e4a1) (can be empty or non-existent)

## Installation
```shell
git clone git@github.com:flottegurke/ssh-tui.git
cd ssh-tui
pip install .
```

## Credits
- Layout: heavily inspired by [sshs](https://github.com/quantumsheep/sshs)
- Theme: powered by [Catppuccin Mocha](https://github.com/catppuccin/catppuccin)