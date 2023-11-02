"""Class to display terminal outputs.

Author: Zak Oster zcoster@ksu.edu
Version: 0.1
"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from PIL import ImageTk, Image
from threading import Thread, Event
from time import sleep

from certificate_maker.src.data.certificate import create_certificates


class TerminalPanel(tk.Frame):
    """Class to display loading options."""

    def __init__(self, master) -> None:
        """Constructor to initialize the menu panel."""
        self.__master = master
        ttk.Frame.__init__(self, master=self.__master)

        self.terminal = scrolledtext.ScrolledText(
            self.__master,
            wrap=tk.WORD,
            font=("Arial", 14)
        )
        self.terminal.grid(row=0, column=1, padx=2, pady=2, sticky="NSEW")
        self.terminal.insert(tk.INSERT, "Program Output:\n")
        self.terminal.configure(state ="disabled")
    
    def print_message(self, message):
        self.terminal.configure(state="normal")
        self.terminal.insert(tk.INSERT, f"\n{message}\n")
        self.terminal.configure(state="disabled")
