"""File selection tile with browse and drag-and-drop support."""

import os
from collections.abc import Callable
from dataclasses import dataclass
import tkinter as tk
from typing import Any
from tkinterdnd2 import COPY, DND_FILES, REFUSE_DROP

from certificate_maker.src.gui.theme import (
    ACCENT,
    BACKGROUND,
    BORDER,
    DROP_BORDER,
    DROP_SURFACE,
    SURFACE,
    SURFACE_HOVER,
    SURFACE_RAISED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
)
from certificate_maker.src.gui.widgets import FileIcon, RoundedButton, RoundedCard


@dataclass
class _DropFeedback:
    status: str = "Drop a file here"
    metadata: str = "or choose Browse"
    status_color: str = TEXT_PRIMARY
    metadata_color: str = TEXT_SECONDARY
    drag_targets: int = 0
    reset_id: str | None = None


class FileSelector(RoundedCard):
    """A file tile that owns its presentation and drag-and-drop feedback."""

    def __init__(
        self,
        master: Any,
        label_text: str,
        on_file_selected: Callable[[str | None], None],
        log_message: Callable[[str], None],
    ) -> None:
        super().__init__(
            master,
            background=SURFACE,
            canvas_background=BACKGROUND,
            outline=BORDER,
            height=90,
            radius=16,
        )
        self.__label_text = label_text
        self.__on_file_selected = on_file_selected
        self.__log_message = log_message
        self.__drop_feedback = _DropFeedback()

        self.content.grid_columnconfigure(0, weight=0, minsize=190)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_columnconfigure(2, weight=0)
        self.content.grid_rowconfigure(0, weight=1)

        title_label = tk.Label(
            self.content,
            text=label_text,
            font=("Arial", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=SURFACE,
            anchor="w",
            justify="left",
        )
        title_label.grid(row=0, column=0, padx=(12, 14), pady=6, sticky="EW")

        self.__drop_zone = RoundedCard(
            self.content,
            background=DROP_SURFACE,
            canvas_background=SURFACE,
            outline=DROP_BORDER,
            height=66,
            radius=13,
            inset=6,
        )
        self.__drop_zone.grid(row=0, column=1, padx=4, pady=7, sticky="EW")
        self.__drop_zone.content.grid_columnconfigure(1, weight=1)
        self.__drop_zone.content.grid_rowconfigure(0, weight=1)

        icon = FileIcon(self.__drop_zone.content)
        icon.grid(row=0, column=0, rowspan=2, padx=(10, 8), pady=6)

        self.__status_label = tk.Label(
            self.__drop_zone.content,
            text=self.__drop_feedback.status,
            font=("Arial", 15, "bold"),
            justify="left",
            anchor="w",
            fg=TEXT_PRIMARY,
            bg=DROP_SURFACE,
        )
        self.__status_label.grid(
            row=0, column=1, padx=(0, 10), pady=(4, 0), sticky="SEW"
        )

        self.__metadata_label = tk.Label(
            self.__drop_zone.content,
            text=self.__drop_feedback.metadata,
            font=("Arial", 12),
            justify="left",
            anchor="w",
            fg=TEXT_SECONDARY,
            bg=DROP_SURFACE,
        )
        self.__metadata_label.grid(
            row=1, column=1, padx=(0, 10), pady=(0, 4), sticky="NEW"
        )

        browse_button = RoundedButton(
            self.content,
            text="Browse",
            command=lambda: self.__on_file_selected(None),
            background=SURFACE_RAISED,
            foreground=TEXT_PRIMARY,
            hover_background=SURFACE_HOVER,
            active_background=BORDER,
            canvas_background=SURFACE,
            width=106,
            height=42,
            radius=11,
            font=("Arial", 13, "bold"),
        )
        browse_button.grid(row=0, column=2, padx=(10, 10), pady=4)

        for widget in (
            self,
            self.content,
            self.__drop_zone,
            self.__drop_zone.content,
            title_label,
            icon,
            self.__status_label,
            self.__metadata_label,
            browse_button,
        ):
            self.__register_drop_target(widget)

    def set_file_status(
        self,
        filename: str,
        metadata: str,
        *,
        selected: bool = False,
    ) -> None:
        feedback = self.__drop_feedback
        feedback.status = filename
        feedback.metadata = metadata
        feedback.status_color = TEXT_PRIMARY if selected else TEXT_SECONDARY
        feedback.metadata_color = TEXT_SECONDARY
        self.__render_status()

    def __render_status(self) -> None:
        feedback = self.__drop_feedback
        self.__status_label.configure(
            text=feedback.status,
            fg=feedback.status_color,
            bg=DROP_SURFACE,
        )
        self.__metadata_label.configure(
            text=feedback.metadata,
            fg=feedback.metadata_color,
            bg=DROP_SURFACE,
        )

    def __restore_drop_feedback(self) -> None:
        feedback = self.__drop_feedback
        feedback.reset_id = None
        feedback.drag_targets = 0
        self.set_outline(BORDER)
        self.__drop_zone.set_outline(DROP_BORDER)
        self.__render_status()

    def __on_drag_enter(self, event: Any) -> str:
        feedback = self.__drop_feedback
        feedback.drag_targets += 1
        if feedback.reset_id is not None:
            self.after_cancel(feedback.reset_id)
            feedback.reset_id = None
        if feedback.drag_targets == 1:
            self.set_outline(ACCENT)
            self.__drop_zone.set_outline(ACCENT)
            self.__status_label.configure(
                fg=TEXT_PRIMARY,
                text=f"Release to add {self.__label_text}",
            )
            self.__metadata_label.configure(
                fg=TEXT_PRIMARY,
                text="Drop a single file in this tile",
            )
        return COPY

    def __on_drag_leave(self, event: Any) -> str:
        feedback = self.__drop_feedback
        feedback.drag_targets = max(0, feedback.drag_targets - 1)
        if feedback.drag_targets == 0:
            feedback.reset_id = self.after(50, self.__restore_drop_feedback)
        return COPY

    def __on_drop(self, event: Any) -> str:
        try:
            paths = self.winfo_toplevel().tk.splitlist(event.data)
        except tk.TclError as error:
            self.__reject_drop(
                f"Invalid drop. Use one {self.__label_text} file.",
                "Choose a file using Browse or drop it here.",
                f"Drop rejected for {self.__label_text}: could not read the file path ({error}).",
            )
            return REFUSE_DROP

        if len(paths) != 1:
            self.__reject_drop(
                f"Drop one {self.__label_text} file at a time.",
                "This tile accepts a single file.",
                f"Drop rejected for {self.__label_text}: select exactly one file at a time.",
            )
            return REFUSE_DROP

        selected_file = paths[0]
        if not os.path.isfile(selected_file):
            self.__reject_drop(
                f"Drop a valid {self.__label_text} file here.",
                "Choose a file using Browse or drop it here.",
                f"Drop rejected for {self.__label_text}: `{selected_file}` is not a file.",
            )
            return REFUSE_DROP

        self.__on_file_selected(selected_file)
        self.__restore_drop_feedback()
        return COPY

    def __reject_drop(
        self,
        status: str,
        metadata: str,
        log_message: str,
    ) -> None:
        feedback = self.__drop_feedback
        feedback.status = status
        feedback.metadata = metadata
        self.__log_message(log_message)
        self.__restore_drop_feedback()

    def __register_drop_target(self, widget: Any) -> None:
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind("<<DropEnter>>", self.__on_drag_enter)
        widget.dnd_bind("<<DropLeave>>", self.__on_drag_leave)
        widget.dnd_bind("<<Drop>>", self.__on_drop)
