from collections.abc import Callable
import tkinter as tk
from typing import Any

from certificate_maker.src.gui.theme import (
    BACKGROUND,
    BORDER,
    DROP_SURFACE,
    ACCENT,
    STATUS_ERROR,
    SURFACE,
    TEXT_SECONDARY,
)


def _draw_rounded_fill(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float,
    color: str,
) -> None:
    if x2 <= x1 or y2 <= y1:
        return

    radius = min(radius, (x2 - x1) / 2, (y2 - y1) / 2)
    tags = ("rounded-surface",)
    canvas.create_rectangle(
        x1 + radius,
        y1,
        x2 - radius,
        y2,
        fill=color,
        outline=color,
        tags=tags,
    )
    canvas.create_rectangle(
        x1,
        y1 + radius,
        x2,
        y2 - radius,
        fill=color,
        outline=color,
        tags=tags,
    )
    corners = (
        (x1, y1, x1 + 2 * radius, y1 + 2 * radius, 90),
        (x2 - 2 * radius, y1, x2, y1 + 2 * radius, 0),
        (x2 - 2 * radius, y2 - 2 * radius, x2, y2, 270),
        (x1, y2 - 2 * radius, x1 + 2 * radius, y2, 180),
    )
    for left, top, right, bottom, start in corners:
        canvas.create_arc(
            left,
            top,
            right,
            bottom,
            start=start,
            extent=90,
            style=tk.PIESLICE,
            fill=color,
            outline=color,
            tags=tags,
        )


class FileIcon(tk.Canvas):
    def __init__(
        self,
        master: Any,
        *,
        background: str = DROP_SURFACE,
        foreground: str = TEXT_SECONDARY,
    ) -> None:
        super().__init__(
            master,
            width=34,
            height=40,
            bg=background,
            borderwidth=0,
            highlightthickness=0,
        )
        self.create_polygon(
            8,
            4,
            19,
            4,
            26,
            11,
            26,
            36,
            8,
            36,
            fill=background,
            outline=foreground,
            width=2,
            joinstyle=tk.ROUND,
        )
        self.create_line(19, 4, 19, 11, fill=foreground, width=2)
        self.create_line(19, 11, 26, 11, fill=foreground, width=2)
        self.create_line(12, 19, 22, 19, fill=foreground, width=2)
        self.create_line(12, 25, 22, 25, fill=foreground, width=2)
        self.create_line(12, 31, 19, 31, fill=foreground, width=2)


class RoundedButton(tk.Canvas):
    def __init__(
        self,
        master: Any,
        text: str,
        command: Callable[[], None],
        *,
        background: str,
        foreground: str,
        hover_background: str,
        active_background: str | None = None,
        selected_background: str | None = None,
        selected_foreground: str | None = None,
        canvas_background: str = BACKGROUND,
        width: int = 120,
        height: int = 44,
        radius: int = 12,
        font: tuple[str, int, str] = ("Arial", 12, "bold"),
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            bg=canvas_background,
            borderwidth=0,
            highlightthickness=0,
            takefocus=True,
            cursor="arrow",
        )
        self.__text = text
        self.__command = command
        self.__background = background
        self.__foreground = foreground
        self.__hover_background = hover_background
        self.__active_background = active_background or hover_background
        self.__selected_background = selected_background or background
        self.__selected_foreground = selected_foreground or foreground
        self.__radius = radius
        self.__font = font
        self.__hovered = False
        self.__pressed = False
        self.__selected = False

        self.bind("<Configure>", self.__draw)
        self.bind("<Enter>", self.__on_enter)
        self.bind("<Leave>", self.__on_leave)
        self.bind("<ButtonPress-1>", self.__on_press)
        self.bind("<ButtonRelease-1>", self.__on_release)
        self.bind("<Return>", self.__on_key)
        self.bind("<space>", self.__on_key)
        self.bind("<FocusIn>", lambda event: self.__draw())
        self.bind("<FocusOut>", lambda event: self.__draw())

    def set_selected(self, selected: bool) -> None:
        self.__selected = selected
        self.__draw()

    def set_text(self, text: str) -> None:
        self.__text = text
        self.__draw()

    def __draw(self, event: Any = None) -> None:
        width = event.width if event is not None else self.winfo_width()
        height = event.height if event is not None else self.winfo_height()
        if width <= 1 or height <= 1:
            return

        self.delete("rounded-surface")
        self.delete("button-label")
        background = self.__background
        foreground = self.__foreground
        if self.__selected:
            background = self.__selected_background
            foreground = self.__selected_foreground
        elif self.__pressed:
            background = self.__active_background
        elif self.__hovered:
            background = self.__hover_background

        outline = None
        if self.focus_get() is self:
            outline = BORDER
        if outline:
            _draw_rounded_fill(
                self, 0, 0, width - 1, height - 1, self.__radius, outline
            )
            _draw_rounded_fill(
                self,
                1,
                1,
                width - 2,
                height - 2,
                max(0, self.__radius - 1),
                background,
            )
        else:
            _draw_rounded_fill(
                self, 0, 0, width - 1, height - 1, self.__radius, background
            )
        self.create_text(
            width / 2,
            height / 2,
            text=self.__text,
            fill=foreground,
            font=self.__font,
            tags=("button-label",),
        )

    def __on_enter(self, event: Any) -> None:
        self.__hovered = True
        self.__draw()

    def __on_leave(self, event: Any) -> None:
        self.__hovered = False
        self.__pressed = False
        self.__draw()

    def __on_press(self, event: Any) -> str:
        self.__pressed = True
        self.focus_set()
        self.__draw()
        return "break"

    def __on_release(self, event: Any) -> str:
        was_pressed = self.__pressed
        self.__pressed = False
        self.__draw()
        if was_pressed and 0 <= event.x <= self.winfo_width():
            if 0 <= event.y <= self.winfo_height():
                self.__command()
        return "break"

    def __on_key(self, event: Any) -> str:
        self.__command()
        return "break"


class RoundedCard(tk.Canvas):
    def __init__(
        self,
        master: Any,
        *,
        background: str = SURFACE,
        canvas_background: str = BACKGROUND,
        outline: str = BORDER,
        width: int = 500,
        height: int = 78,
        radius: int = 16,
        inset: int = 8,
    ) -> None:
        super().__init__(
            master,
            width=width,
            height=height,
            bg=canvas_background,
            borderwidth=0,
            highlightthickness=0,
        )
        self.content = tk.Frame(
            self, bg=background, borderwidth=0, highlightthickness=0
        )
        self.__background = background
        self.__outline = outline
        self.__radius = radius
        self.__inset = inset
        self.__content_window = self.create_window(
            inset,
            inset // 2,
            window=self.content,
            anchor="nw",
        )
        self.bind("<Configure>", self.__resize)

    def set_outline(self, outline: str) -> None:
        self.__outline = outline
        self.__draw(self.winfo_width(), self.winfo_height())

    def __resize(self, event: Any) -> None:
        self.coords(self.__content_window, self.__inset, self.__inset // 2)
        self.itemconfigure(
            self.__content_window,
            width=max(1, event.width - 2 * self.__inset),
            height=max(1, event.height - self.__inset),
        )
        self.__draw(event.width, event.height)

    def __draw(self, width: int, height: int) -> None:
        self.delete("rounded-surface")
        _draw_rounded_fill(
            self,
            0,
            0,
            width - 1,
            height - 1,
            self.__radius,
            self.__outline,
        )
        _draw_rounded_fill(
            self,
            1,
            1,
            width - 2,
            height - 2,
            max(0, self.__radius - 1),
            self.__background,
        )
        self.tag_lower("rounded-surface")


class StatusBanner(tk.Canvas):
    def __init__(self, master: Any) -> None:
        super().__init__(
            master,
            width=470,
            height=56,
            bg=BACKGROUND,
            borderwidth=0,
            highlightthickness=0,
            takefocus=False,
            cursor="arrow",
        )
        self.__message = ""
        self.__background = ACCENT
        self.bind("<Configure>", self.__draw)

    def set_status(self, message: str, succeeded: bool) -> None:
        self.__message = message
        self.__background = ACCENT if succeeded else STATUS_ERROR
        self.__draw()

    def __draw(self, event: Any = None) -> None:
        width = event.width if event is not None else self.winfo_width()
        height = event.height if event is not None else self.winfo_height()
        if width <= 1 or height <= 1:
            return

        self.delete("rounded-surface")
        self.delete("status-message")
        _draw_rounded_fill(self, 0, 0, width - 1, height - 1, 14, self.__background)
        self.create_text(
            width / 2,
            height / 2,
            text=self.__message,
            fill=BACKGROUND,
            font=("Arial", 13, "bold"),
            width=max(1, width - 32),
            tags=("status-message",),
        )
