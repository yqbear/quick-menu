"""Provide a simple means to create text menus for a console application.

Example:

    This example shows two ways to create a menu, one for the submenu and the other
    for the main menu.

        from quick_menu.menu import Menu, MenuItem

        def func1(val=1):
            print("func1: val =", val)
            input("Press [Enter] to continue")

        submenu = Menu(
            "Submenu",
            menu_items=[
                MenuItem("1", "Do func1", action=func1),
                MenuItem("X", "Go back", is_exit=True),
            ]
        )
        menu = (
            Menu("Some Title")
            .add(MenuItem("1", "Func1 default", action=func1))
            .add(MenuItem("2", "Func1 with val", action=func1, action_args={"val": 4}))
            .add(MenuItem("S", "Submenu", action=submenu.run))
            .add(MenuItem("X", "Exit", is_exit=True))
        )

        menu.run()
"""
import os
from dataclasses import dataclass, field
from typing import Any, Callable, ClassVar, Dict, List, Optional, Tuple

from typing_extensions import Self


@dataclass
class MenuItem:
    """A menu item to add to a menu.

    The menu item can optionally call a function or start a submenu. A menu item can
    also be an exit item which exits the curren menu.

    Parameters:
        choice:       The string used to select the menu item.
        label:        The text label displayed for the menu item.
        action:       An optional function to be called when the menu item is selected.
        action_args:  Arguments to pass to a menu item action.
        is_exit:      Whether or not this menu item exits the current menu
    """

    VALID_UPDATE_FIELDS: ClassVar[Tuple[str, ...]] = ("label", "action", "action_args")

    choice: str
    label: str
    action: Optional[Callable[..., None]] = None
    action_args: dict = field(default_factory=dict)
    is_exit: bool = False

    def select(self) -> bool:
        """Select the menu item.

        This selects the `MenuItem` which runs any associated action with kwargs and
        then returns whether or not selecting this item should tell the current menu to
        exit.

        Returns:
            True if the item is an exit item; False otherwise
        """
        if self.action:
            self.action(**self.action_args)
        return not self.is_exit

    def update(self, **kwargs: Dict[str, Any]) -> None:
        """Update menu item fields.

        Any key matching a field to be updated is replaced with the new vlaue. Any
        remaining key/value pairs are used to update the `action_args`.

        Paramaters:
            kwargs: A dict with fields to be updated.
        """
        for name in MenuItem.VALID_UPDATE_FIELDS:
            val = kwargs.pop(name, None)
            if val:
                setattr(self, name, val)
        # Anything else is used to update kwargs
        self.action_args.update(kwargs)


class Menu:
    """A menu that can be displayed and accepts user selections."""

    BANNER_WIDTH: int = 40

    def __init__(
        self,
        title: str,
        menu_items: Optional[List[MenuItem]] = None,
        prompt: Optional[str] = None,
        auto_clear: Optional[bool] = None,
    ):
        """Create a new menu.

        Parameters:
            title: The title to display at the top of the menu.
            menu_items: An optional list of `MenuItem` to add to the menu.
            prompt:     An optional custom prompt for input.
            auto_clear:  Whether or not to clear the screen before running.
        """
        self.title = title
        self.menu_items: Dict[str, MenuItem] = {}
        if menu_items:
            for menu_item in menu_items:
                self.add(menu_item)
        self.prompt = prompt if prompt else ">> "
        self.auto_clear = auto_clear if auto_clear else True

    def add(self, menu_item: MenuItem) -> Self:
        """Add a new MenuItemq.

        Parameters:
            menu_item: A `MenuItem` instance.

        Returns:
            The `Menu` instance. This allows chaining of the `add` calls. For example:

                    menu.add("1", "First").add("2", "Second")
        """
        if menu_item.is_exit is True:
            # Check if there is an existing exit since there can be only one
            exit_key = self._exit_choice()
            if exit_key:
                del self.menu_items[exit_key]
        self.menu_items[menu_item.choice.lower()] = menu_item
        self._ensure_one_exit_exists()
        return self

    def display(self) -> str:
        """Return the Menu display as a string."""
        title_length = len(self.title) + 2
        right_length = (Menu.BANNER_WIDTH - title_length) // 2
        left_length = Menu.BANNER_WIDTH - title_length - right_length
        out = [" ".join(["=" * left_length, self.title, "=" * right_length])]
        for key in sorted(self.menu_items):
            menu_item = self.menu_items[key]
            out.append(f"{menu_item.choice}: {menu_item.label}")
        out.append("=" * Menu.BANNER_WIDTH)
        return "\n".join(out)

    def run(self) -> None:
        """Display the `Menu` and start a loop to process selections."""
        running = True
        while running:
            if self.auto_clear:
                Menu.clear()
            print(self.display())
            choice = input(self.prompt)
            key = choice.lower()
            if key in self.menu_items:
                running = self.menu_items[key].select()
            else:
                print(f"Invalid choice: {choice}")
                input("\nPress [Enter] to continue")

    def update(self, choice: str, **kwargs: Dict[str, Any]) -> None:
        menu_item = self.menu_items.get(choice.lower())
        if menu_item:
            menu_item.update(**kwargs)

    def _exit_choice(self) -> Optional[str]:
        exit_keys = [k for k, v in self.menu_items.items() if v.is_exit is True]
        if exit_keys:
            return exit_keys[0]
        return None

    def _ensure_one_exit_exists(self) -> None:
        exit_key = self._exit_choice()
        if not exit_key:
            self.menu_items["x"] = MenuItem("X", "Exit", is_exit=True)

    @staticmethod
    def clear() -> None:
        """Calls a system method to clear the console."""
        os.system("clear" if os.name == "posix" else "cls")
