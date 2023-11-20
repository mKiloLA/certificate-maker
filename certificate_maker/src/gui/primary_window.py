import tkinter as tk
from tkinter import ttk
from certificate_maker.src.gui.tab_panel import TabPanel
from certificate_maker.src.gui.terminal_panel import TerminalPanel


class PrimaryWindow(tk.Tk):
    """Class to represent the main window."""

    def __init__(self) -> None:
        """Constructor to initialize the window.

        __init__ does not take any args, and only one instance
        of the class should exist at a time.
        """
        tk.Tk.__init__(self)
        self.__style: ttk.Style = ttk.Style(self)

        self.minsize(width=900, height=400)
        self.maxsize(width=900, height=400)
        self.title("Certificate Maker")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)

        self.__side = TerminalPanel(self)
        self.__side.grid(row=0, column=1, padx=10, pady=10, sticky="NSEW")

        self.__main = TabPanel(self, self.__side)
        self.__main.grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")

