# -*- coding: utf-8 -*-
from galaxies.src.gui.main_menu import WindowMainMenu


def cli_entry_point():
    print("Hello CLI !")


def gui_entry_point():
    WindowMainMenu()


if __name__ == '__main__':
    gui_entry_point()
