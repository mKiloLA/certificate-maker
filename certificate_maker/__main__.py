from certificate_maker.src.gui.primary_window import PrimaryWindow
# from certificate_maker.src.data.certificate import create_certificates
import logging

logging.basicConfig(
    filemode="w",
    filename="Certificates/CertificatesToCheck.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    # create_certificates("zoom", "master")
    PrimaryWindow().mainloop()


if __name__ == "__main__":
    main()
