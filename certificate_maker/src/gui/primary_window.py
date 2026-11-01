from tkinter import ttk
from tkinterdnd2 import TkinterDnD
from certificate_maker.src.gui.tab_panel import TabPanel
from certificate_maker.src.gui.terminal_panel import TerminalPanel
from certificate_maker.src.gui.theme import BACKGROUND, configure_styles
from certificate_maker.src.gui.widgets import StatusBanner


class PrimaryWindow(TkinterDnD.Tk):
    """Class to represent the main window."""

    def __init__(self) -> None:
        """Constructor to initialize the window.

        __init__ does not take any args, and only one instance
        of the class should exist at a time.
        """
        TkinterDnD.Tk.__init__(self)
        self.__style: ttk.Style = ttk.Style(self)
        configure_styles(self.__style)

        self.title("Certificate Maker")
        self.resizable(True, True)
        self.configure(bg=BACKGROUND)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = min(1400, int(screen_width * 0.94))
        window_height = min(660, int(screen_height * 0.94))
        self.minsize(
            width=min(760, window_width),
            height=window_height,
        )

        self.grid_rowconfigure(0, weight=1, minsize=360)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.__side = TerminalPanel(self, self.__set_activity_expanded)
        self.__side.grid(row=1, column=0, padx=18, pady=(4, 14), sticky="NSEW")

        self.__main = TabPanel(
            self,
            self.__side,
            show_status_banner=self.show_status_banner,
        )
        self.__main.grid(row=0, column=0, padx=18, pady=(16, 8), sticky="NSEW")

        self.__status_banner = StatusBanner(self)
        self.__status_banner_after: str | None = None
        self.__status_banner_generation = 0

        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

    def show_status_banner(self, message: str, succeeded: bool) -> None:
        if self.__status_banner_after is not None:
            self.after_cancel(self.__status_banner_after)
            self.__status_banner_after = None

        self.__status_banner_generation += 1
        generation = self.__status_banner_generation
        self.__status_banner.set_status(message, succeeded)
        self.__status_banner.place(relx=0.5, rely=1.0, anchor="s", y=70)
        self.__slide_status_banner_up(generation, 70)

    def __slide_status_banner_up(self, generation: int, offset: int) -> None:
        if generation != self.__status_banner_generation:
            return
        self.__status_banner_after = None
        offset = max(-18, offset - 12)
        self.__status_banner.place(relx=0.5, rely=1.0, anchor="s", y=offset)
        if offset > -18:
            self.__status_banner_after = self.after(
                15,
                lambda: self.__slide_status_banner_up(generation, offset),
            )
        else:
            self.__status_banner_after = self.after(
                2800,
                lambda: self.__slide_status_banner_down(generation, offset),
            )

    def __slide_status_banner_down(self, generation: int, offset: int) -> None:
        if generation != self.__status_banner_generation:
            return
        self.__status_banner_after = None
        offset = min(70, offset + 12)
        self.__status_banner.place(relx=0.5, rely=1.0, anchor="s", y=offset)
        if offset < 70:
            self.__status_banner_after = self.after(
                15,
                lambda: self.__slide_status_banner_down(generation, offset),
            )
        else:
            self.__status_banner.place_forget()

    def __set_activity_expanded(self, expanded: bool) -> None:
        if expanded:
            self.grid_rowconfigure(0, weight=0, minsize=360)
            self.grid_rowconfigure(1, weight=1, minsize=100)
        else:
            self.grid_rowconfigure(0, weight=1, minsize=360)
            self.grid_rowconfigure(1, weight=0, minsize=0)
