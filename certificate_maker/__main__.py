from certificate_maker.src.gui.primary_window import PrimaryWindow
from certificate_maker.src.data.certificate import create_certificates


def main() -> None:
    PrimaryWindow().mainloop()


if __name__ == "__main__":
    main()
    # create_certificates(r"/Users/wendioster/Documents/Comedian of Law/playground/certificate-maker/references/zoom_attendence.csv", r"/Users/wendioster/Documents/Comedian of Law/playground/certificate-maker/references/master_webinar_list.xlsx")
