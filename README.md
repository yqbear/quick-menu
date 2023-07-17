# quick-menu

[![PyPI - Version](https://img.shields.io/pypi/v/quick-menu.svg)](https://pypi.org/project/quick-menu)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/quick-menu.svg)](https://pypi.org/project/quick-menu)

-----

This is a simple package to create text menus for use in console applications.

## Usage

A menu can be created quickly that can call a function with or without a value. An exit
item is automatically added to the menu.

### Create a Quick Menu

```python
from quick_menu.menu import Menu, MenuItem

def func(val=1):
    print("func1: val =", val)
    input("Press [Enter] to continue")

menu = Menu(
    "Simple Menu",
    menu_items=[
        MenuItem("1", "Func default", action=func),
        MenuItem("2", "Func with val=4", action=func, action_args={"val": 4}),
    ]
)

menu.run()
```

### Output

```
============== Simple Menu =============
1: Func default
2: Func with val=4
X: Exit
========================================
>> 1
func1: val = 1
Press [Enter] to continue

============== Simple Menu =============
1: Func default
2: Func with val=4
X: Exit
========================================
>> 2
func1: val = 4
Press [Enter] to continue
```

## Documentation

The [documentation](https://yqbear.github.io/quick-menu) is made with [Material for MkDocs](https://github.com/squidfunk/mkdocs-material) and is hosted by [GitHub Pages](https://docs.github.com/en/pages).

## Installation

```console
pip install quick-menu
```

## License

`quick-menu` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
