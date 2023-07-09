from pypdf import PdfReader, PdfWriter
from certificate_maker.src.data.webinar import Webinar

from certificate_maker.src.gui.primary_window import PrimaryWindow

from datetime import datetime, date
from certificate_maker.src.data.ref import states_dict

def main() -> None:
    """Main Function.

    Main routine that is called when program begins.

    Args:
        None

    Returns:
        None
    """
    PrimaryWindow().mainloop()


if __name__ == "__main__":
    main()
    