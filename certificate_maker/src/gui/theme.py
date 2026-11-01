from tkinter import ttk

BACKGROUND = "#111820"
SURFACE = "#1a232c"
SURFACE_RAISED = "#202c36"
SURFACE_HOVER = "#293841"
BORDER = "#33414b"
DROP_SURFACE = "#2b343b"
DROP_BORDER = "#66747d"
TEXT_PRIMARY = "#edf2f2"
TEXT_SECONDARY = "#a8b5bc"
ACCENT = "#65c6aa"
ACCENT_HOVER = "#7bd6bb"
ACCENT_PRESSED = "#4eac92"
STATUS_ERROR = "#e4777f"
LOG_BACKGROUND = "#141b22"


def configure_styles(style: ttk.Style) -> None:
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(".", background=BACKGROUND, foreground=TEXT_PRIMARY)
    style.configure("TFrame", background=BACKGROUND, borderwidth=0)
    style.configure("TLabel", background=BACKGROUND, foreground=TEXT_PRIMARY)
    style.configure(
        "PageTitle.TLabel",
        background=BACKGROUND,
        foreground=TEXT_PRIMARY,
        font=("Arial", 22, "bold"),
    )
    style.configure(
        "PageDescription.TLabel",
        background=BACKGROUND,
        foreground=TEXT_SECONDARY,
        font=("Arial", 12),
    )
    style.configure(
        "Activity.Vertical.TScrollbar",
        background=SURFACE_RAISED,
        darkcolor=SURFACE_RAISED,
        lightcolor=SURFACE_RAISED,
        troughcolor=LOG_BACKGROUND,
        bordercolor=LOG_BACKGROUND,
        arrowcolor=TEXT_SECONDARY,
        width=12,
    )
    style.map(
        "Activity.Vertical.TScrollbar",
        background=[("pressed", ACCENT_PRESSED), ("active", ACCENT)],
    )
