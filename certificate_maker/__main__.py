from certificate_maker.src.gui.primary_window import PrimaryWindow
from certificate_maker.src.data.certificate import create_certificates
from certificate_maker.src.data.emails import send_emails
import logging
from os import path

logging.basicConfig(
    filemode="w",
    filename=path.join(path.expanduser('~'), "Certificates/CertificatesToCheck.log"),
    encoding="utf-8",
    level=logging.INFO,
    format="%(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    # zoom = r""
    # master = r""
    # emails = r""
    # create_certificates(zoom, master)
    # send_emails(emails)
    PrimaryWindow().mainloop()


if __name__ == "__main__":
    main()
