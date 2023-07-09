from pypdf import PdfReader, PdfWriter
from certificate_maker.src.data.webinar import Webinar
from certificate_maker.src.data.ref import states_dict

from datetime import datetime, date


def create_certificates(zoom_file, webinar_file):
    webinar = Webinar(zoom_file, webinar_file)
    for person in webinar.attendees:
        for index, state in enumerate(person.states):
            state_abbrev = list(states_dict.keys())[list(states_dict.values()).index(state)]
            try:
                approval_information = webinar.cle_class.approvals[state_abbrev]
            except:
                approval_information = "Not approved in this state."
            certificate_form = {
                "name": person.name,
                "state": state,
                "bar_number": "#{}".format(person.bar_numbers[index]),
                "completion_date": webinar.cle_class.cle_date.strftime("%b %d, %Y"),
                "attendence_hours": "{:.1f}h".format(person.total_time.total_seconds() / 3600),
                "attendence_time_range": "",
                "cle_approvals": "Course #{} approved in {} for {} hours.".format(approval_information[0], state, approval_information[1]),
                "certification_date": date.today().strftime("%b %d, %Y"),
            }
        
            reader = PdfReader("references/certificate_form.pdf")
            writer = PdfWriter()
            page = reader.pages[0]
            fields = reader.get_fields()
            writer.append(reader)
            writer.update_page_form_field_values(
                writer.pages[0], certificate_form, 1
            )

            # write "output" to pypdf-output.pdf
            with open("output-certificates/{}-{}.pdf".format(person.name.replace(" ", "_"), person.email), "wb") as output_stream:
                writer.write(output_stream)

