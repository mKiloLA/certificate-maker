from certificate_maker.src.gui.primary_window import PrimaryWindow
import logging
from os import path

logging.basicConfig(
    filemode="w",
    filename=path.join(
        path.expanduser("~"), "CertificateMaker/CertificatesToCheck.log"
    ),
    encoding="utf-8",
    level=logging.INFO,
    format="%(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    PrimaryWindow().mainloop()


if __name__ == "__main__":
    main()
