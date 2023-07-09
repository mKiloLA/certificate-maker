import os
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
            og_name_list = webinar.cle_class.cle_name.split(" ")
            first_name_list = []
            overflow_name_list = []
            total_length = 0
            for name in og_name_list:
                if total_length + len(name) >= 40:
                    overflow_name_list.append(name)
                    total_length+=len(name)
                else:
                    first_name_list.append(name)
                    total_length+=len(name)
            name_1 = " ".join(first_name_list)
            name_2 = " ".join(overflow_name_list)
            certificate_data = {
                "name": person.name,
                "state": state,
                "barnumber": "#{}".format(person.bar_numbers[index]),
                "attendedhours": "{:.2f}".format(
                    person.total_time.total_seconds() / 3600
                ),
                "cledate": webinar.cle_class.cle_date.strftime("%B %d, %Y"),
                "totalhours": approval_information[1],
                "coursenumber": "#{}".format(approval_information[0]),
                "approvalstate": state,
                "credits": approval_information[2],
                "certifieddate": date.today().strftime("%m/%d/%Y"),
                "clename": name_1,
                "overflow": name_2 if len(name_2) > 0 else "",
            }

            reader = PdfReader("references/certificate_form_empty.pdf")
            writer = PdfWriter()
            fields = reader.get_fields()
            writer.append(reader)
            writer.update_page_form_field_values(writer.get_page(0), certificate_data, 1)

            # write "output" to pypdf-output.pdf
            os.makedirs("output-certificates", exist_ok=True)
            with open(
                "output-certificates/{}-{}-{}.pdf".format(
                    person.name.replace(" ", "_"), state, person.email
                ),
                "wb",
            ) as output_stream:
                writer.write(output_stream)
