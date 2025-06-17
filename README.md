# ssh-tui
ssh-tui is a sleek and minimal terminal user interface (TUI) for managing SSH connections.

## Features
- Quickly filter through SSH connections
- Manage SSH connections from within the TUI (add, edit, delete)
- Connections get stored in your `~/.ssh/config` file

## Requirements
- Python 3.11+
- [textual](https://github.com/Textualize/textual)
- [rich](https://github.com/Textualize/rich)
- A [functional `~/.ssh/config file`](https://gist.github.com/numberwhun/d986bb536af15c5fccdcd5dfa656e4a1) (can be empty or non-existent)
> [!TIP]
> textual and rich are automatically installed as dependencies when you initialize ssh-tui using `pip`.

## Installation
```shell
git clone git@github.com:flottegurke/ssh-tui.git
cd ssh-tui
pip install .
```

## Usage
```shell
ssh-tui
```
- `Typing`: Filter/Search connections
- `Arrow up` / `Arrow down`: Navigate through results (connections)
- `Enter`: Connect to selected connection
- `Ctrl + c` / `Ctrl + q` / `Escape`: Exit the application
- `Ctrl + a`: Add a new connection
- `Ctrl + e`: Edit the selected connection
- `Ctrl + d`: Delete the selected connection
- While popup menus are open:
  - `Tab` / `Shift + Tab`: Navigate between inputs
  - `Ctrl + y`: Submit the form
  - `Ctrl + n` / `Escape`: Cancel the form
  - `Ctrl + q`: Exit the whole application

## Credits
- Layout: heavily inspired by [sshs](https://github.com/quantumsheep/sshs)
- Theme: powered by [Catppuccin Mocha](https://github.com/catppuccin/catppuccin)