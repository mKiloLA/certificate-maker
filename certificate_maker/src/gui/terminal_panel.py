"""Class to display terminal outputs.

Author: Zak Oster zc9oster@gmail.com
Version: 0.1
"""

from datetime import datetime
from collections.abc import Callable
import tkinter as tk
from tkinter import ttk
from typing import Any

from certificate_maker.src.gui.theme import (
    ACCENT,
    BACKGROUND,
    BORDER,
    LOG_BACKGROUND,
    SURFACE_HOVER,
    SURFACE_RAISED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from certificate_maker.src.gui.widgets import RoundedButton


class TerminalPanel(tk.Frame):
    """Class to display loading options."""

    def __init__(
        self, master: Any, on_expanded_changed: Callable[[bool], None]
    ) -> None:
        """Constructor to initialize the menu panel."""
        super().__init__(master)
        self.configure(bg=BACKGROUND)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.__expanded = False
        self.__on_expanded_changed = on_expanded_changed

        heading = tk.Label(
            self,
            text="Activity Logs",
            font=("Arial", 14, "bold"),
            fg=ACCENT,
            bg=BACKGROUND,
            anchor="w",
        )
        heading.grid(row=0, column=0, sticky="W")
        self.__toggle_button = RoundedButton(
            self,
            text="Show log",
            command=self.__toggle_expanded,
            background=SURFACE_RAISED,
            foreground=TEXT_PRIMARY,
            hover_background=SURFACE_HOVER,
            active_background=BORDER,
            canvas_background=BACKGROUND,
            width=106,
            height=42,
            radius=11,
            font=("Arial", 13, "bold"),
        )
        self.__toggle_button.grid(row=0, column=1, sticky="E")

        self.__log_frame = tk.Frame(self, bg=BACKGROUND)
        self.__log_frame.grid(row=1, column=0, columnspan=2, pady=(8, 0), sticky="NSEW")
        self.__log_frame.grid_rowconfigure(0, weight=1)
        self.__log_frame.grid_columnconfigure(0, weight=1)

        self.terminal = tk.Text(
            self.__log_frame,
            wrap=tk.WORD,
            font=("TkFixedFont", 14),
            bg=LOG_BACKGROUND,
            fg=TEXT_SECONDARY,
            insertbackground=TEXT_PRIMARY,
            selectbackground=ACCENT,
            selectforeground=BACKGROUND,
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
            padx=14,
            pady=10,
        )
        self.terminal.grid(row=0, column=0, sticky="NSEW")
        scrollbar = ttk.Scrollbar(
            self.__log_frame,
            orient=tk.VERTICAL,
            command=self.terminal.yview,
            style="Activity.Vertical.TScrollbar",
        )
        scrollbar.grid(row=0, column=1, sticky="NS")
        self.terminal.configure(yscrollcommand=scrollbar.set)
        self.terminal.configure(state="disabled")
        self.__log_frame.grid_remove()
        self.print_message("Ready.")

    def __toggle_expanded(self) -> None:
        self.__expanded = not self.__expanded
        if self.__expanded:
            self.__log_frame.grid()
            self.__toggle_button.set_text("Hide log")
        else:
            self.__log_frame.grid_remove()
            self.__toggle_button.set_text("Show log")
        self.__on_expanded_changed(self.__expanded)

    def print_message(self, message: str) -> None:
        """Append a message to the read-only program output area."""
        timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
        lines = message.splitlines() or [""]
        formatted_message = "\n".join(f"[{timestamp}] {line}" for line in lines)
        self.terminal.configure(state="normal")
        self.terminal.insert(tk.END, f"{formatted_message}\n")
        self.terminal.configure(state="disabled")
