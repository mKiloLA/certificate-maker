from certificate_maker.src.gui.primary_window import PrimaryWindow
from certificate_maker.src.data.certificate import create_certificates

def main() -> None:
    PrimaryWindow().mainloop()


if __name__ == "__main__":
    # main()
    create_certificates(r"C:\Python\certificate-maker\references\zoom_attendence.csv", r"C:\Python\certificate-maker\references\master_webinar_list.xlsx")
    