import os  # type: ignore
from unittest.mock import Mock

import pytest  # type: ignore

from quick_menu.menu import Menu, MenuItem


@pytest.fixture
def simple_menu():
    menu = Menu(
        "Simple Menu",
        menu_items=[
            MenuItem("1", "Item 1"),
            MenuItem("X", "Exit", is_exit=True),
        ],
    )
    return menu


def test_menu_item_default():
    menu_item = MenuItem("1", "First Item")
    assert menu_item.choice == "1"
    assert menu_item.label == "First Item"
    assert menu_item.action is None
    assert menu_item.kwargs == {}
    assert menu_item.is_exit is False


def test_run_action():
    fun = Mock()
    menu_item = MenuItem("1", "Call Func", action=fun)
    ret_val = menu_item.select()
    assert fun.called
    assert ret_val is True


def test_run_menu():
    mock_menu = Mock()
    menu_item = MenuItem("1", "Sub Menu", action=mock_menu.run)
    ret_val = menu_item.select()
    assert mock_menu.run.called
    assert ret_val is True


def test_run_with_exit():
    menu_item = MenuItem("1", "Exit", is_exit=True)
    ret_val = menu_item.select()
    assert ret_val is False


def test_menu(monkeypatch):
    responses = iter(["1", "2", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    func1 = Mock()
    func2 = Mock()
    menu = Menu(
        "Title",
        menu_items=[
            MenuItem("1", "First item", action=func1),
            MenuItem("2", "Second item", action=func2),
            MenuItem("X", "Exit", is_exit=True),
        ],
    )
    menu.run()
    assert func1.called
    assert func2.called


def test_submenu(monkeypatch):
    responses = iter(["S", "1", "B", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    func1 = Mock()
    submenu = (
        Menu("Submenu Title").add(MenuItem("1", "Func1", action=func1)).add(MenuItem("B", "Go back", is_exit=True))
    )
    menu = Menu("Menu Title").add(MenuItem("S", "Submenu", action=submenu.run)).add(MenuItem("X", "Exit", is_exit=True))
    menu.run()
    assert func1.called


def test_menu_display():
    expected = """\
============== Menu Title ==============
1: Item 1
S: Submenu
X: Exit
========================================"""
    menu = (
        Menu("Menu Title")
        .add(MenuItem("1", "Item 1"))
        .add(MenuItem("S", "Submenu"))
        .add(MenuItem("X", "Exit", is_exit=True))
    )
    assert menu.display() == expected


def test_func_with_kwargs(monkeypatch):
    responses = iter(["1", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    func1 = Mock()
    menu = Menu(
        "Title",
        menu_items=[
            MenuItem("1", "First item", action=func1, kwargs={"val": 4}),
            MenuItem("X", "Exit", is_exit=True),
        ],
    )
    menu.run()
    func1.assert_called_once_with(val=4)


def test_output(simple_menu, monkeypatch, capsys):
    expected = """\
============== Simple Menu =============
1: Item 1
X: Exit
========================================
"""
    responses = iter(["1", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    simple_menu.run()
    captured = capsys.readouterr()
    assert expected in captured.out


def test_autoclear(simple_menu, monkeypatch, mocker):
    expected_arg = "clear" if os.name == "posix" else "cls"
    mocker.patch("os.system")
    responses = iter(["1", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    simple_menu.run()
    assert os.system.call_count == 2
    os.system.assert_called_with(expected_arg)


def test_no_autoclear(simple_menu, monkeypatch, mocker):
    simple_menu.auto_clear = False
    mocker.patch("os.system")
    responses = iter(["1", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    simple_menu.run()
    assert os.system.call_count == 0


def test_invalid_choice(simple_menu, monkeypatch, capsys):
    expected = "Invalid choice: 5"
    responses = iter(["5", " ", "x"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))
    simple_menu.run()
    captured = capsys.readouterr()
    assert expected in captured.out


def test_sorted_choices():
    expected = """\
============== Menu Title ==============
1: Item 1
2: Item 2
S: Submenu
X: Exit
========================================"""
    menu = Menu(
        "Menu Title",
        menu_items=[
            MenuItem("2", "Item 2"),
            MenuItem("S", "Submenu"),
            MenuItem("X", "Exit", is_exit=True),
            MenuItem("1", "Item 1"),
        ],
    )
    assert menu.display() == expected


def test_add_exit_option_if_missing():
    expected = """\
============== Menu Title ==============
1: Item 1
X: Exit
========================================"""
    menu = Menu(
        "Menu Title",
        menu_items=[
            MenuItem("1", "Item 1"),
        ],
    )
    assert menu.display() == expected


def test_only_one_exit():
    expected = """\
============== Menu Title ==============
1: Item 1
B: Go back
========================================"""
    menu = Menu(
        "Menu Title",
        menu_items=[
            MenuItem("1", "Item 1"),
            MenuItem("B", "Go back", is_exit=True),
        ],
    )
    assert menu.display() == expected
