"""Class to display terminal outputs.

Author: Zak Oster zc9oster@gmail.com
Version: 0.1
"""

import tkinter as tk
from tkinter import scrolledtext
from typing import Any


class TerminalPanel(tk.Frame):
    """Class to display loading options."""

    def __init__(self, master: Any) -> None:
        """Constructor to initialize the menu panel."""
        self.__master = master
        tk.Frame.__init__(self, master=self.__master)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.terminal = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, font=("Arial", 14)
        )
        self.terminal.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")
        self.terminal.insert(tk.INSERT, "Program Output:\n")
        self.terminal.configure(state="disabled")

    def print_message(self, message: str) -> None:
        """Append a message to the read-only program output area."""
        self.terminal.configure(state="normal")
        self.terminal.insert(tk.INSERT, f"\n{message}\n")
        self.terminal.configure(state="disabled")
