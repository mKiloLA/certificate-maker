import tkinter as tk
from tkinter import ttk
from certificate_maker.src.gui.tab_panel import TabPanel


class PrimaryWindow(tk.Tk):
    """Class to represent the main window."""

    def __init__(self) -> None:
        """Constructor to initialize the window.

        __init__ does not take any args, and only one instance
        of the class should exist at a time.
        """
        tk.Tk.__init__(self)
        self.__style: ttk.Style = ttk.Style(self)

        self.minsize(width=800, height=600)
        self.maxsize(width=800, height=600)
        self.title("Certificate Maker")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.__main = None
        self.load_tab_panel(True)

    def load_tab_panel(self, set_create_tab=False) -> None:
        """Loads an instance of the loading panel class.

        Args:
            set_load_tab: bool, determines which tab should
                be displayed when loading the panel

        Returns:
            None
        """
        self.load_panel(TabPanel(self, set_create_tab))

    def load_panel(self, panel) -> None:
        """Loads an instance of a panel.

        Loads a panel into the main panel slot (left side).
        If panel already exists, first destroy current panel.

        Args:
            panel (MenuPanel): likely a menu panel, the panel
                to load on left side of window
        """
        if self.__main is not None:
            self.__main.destroy()
        self.__main = panel
        self.__main.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
