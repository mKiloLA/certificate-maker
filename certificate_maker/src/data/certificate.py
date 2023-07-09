from pypdf import PdfReader, PdfWriter
from certificate_maker.src.data.webinar import Webinar
from certificate_maker.src.data.ref import states_dict

from datetime import datetime, date


def create_certificates(zoom_file, webinar_file):
    webinar = Webinar(zoom_file, webinar_file)
    for person in webinar.attendees:
        for index, state in enumerate(person.states):
            try:
                approval_information = webinar.cle_class.approvals[state]
            except:
                approval_information = ["N/A", "N/A", "N/A"]
            certificate_data = {
                "name": person.name,
                "state": state,
                "bar_number": "#{}".format(person.bar_numbers[index]),
                "attended_hours": "{:.1f}h".format(
                    person.total_time.total_seconds() / 3600
                ),
                "cle_date": webinar.cle_class.cle_date.strftime("%B %d, %Y"),
                "total_hours": approval_information[1],
                "course_number": approval_information[0],
                "approval_state": state,
                "credits": approval_information[2],
                "certified_date": date.today().strftime("%m/%d/%Y"),
                "cle_name": webinar.cle_class.cle_name,
            }

            reader = PdfReader(r"C:\Python\certificate-maker\references\certificate_form.pdf")
            writer = PdfWriter()
            fields = reader.get_fields()
            for field in fields:
                print(field)
            writer.append(reader)
            print(writer.pages[0])
            writer.update_page_form_field_values(writer.get_page(0), certificate_data)

            # # write "output" to pypdf-output.pdf
            # with open(
            #     "output-certificates/{}-{}.pdf".format(
            #         person.name.replace(" ", "_"), person.email
            #     ),
            #     "wb",
            # ) as output_stream:
            #     writer.write(output_stream)
