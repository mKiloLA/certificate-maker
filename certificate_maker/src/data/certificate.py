import os
from pypdf import PdfReader, PdfWriter
from certificate_maker.src.data.webinar import Webinar
import logging

from datetime import date


def create_certificates(zoom_file, webinar_file):
    webinar = Webinar(zoom_file, webinar_file)
    for person in webinar.attendees:
        for index, state in enumerate(person.states):
            try:
                approval_information = webinar.cle_class.approvals[state]
            except:
                logging.error(
                    "Check State Approvals: `{}` has no approval infomation in the state of `{}`.".format(
                        person.name, state
                    )
                )
                approval_information = ["N/A", "N/A", "N/A"]
            og_name_list = webinar.cle_class.cle_name.split(" ")
            first_name_list = []
            overflow_name_list = []
            total_length = 0
            for name in og_name_list:
                if total_length + len(name) >= 40:
                    overflow_name_list.append(name)
                    total_length += len(name)
                else:
                    first_name_list.append(name)
                    total_length += len(name)
            name_1 = " ".join(first_name_list)
            name_2 = " ".join(overflow_name_list)
            certificate_data = {
                "name": person.name,
                "state": state,
                "barnumber": "#{}".format(person.bar_numbers[index]),
                "attendedhours": round_hours(person.total_time, state),
                "cledate": webinar.cle_class.cle_date.strftime("%B %d, %Y"),
                "totalhours": approval_information[1],
                "coursenumber": "#{}".format(approval_information[0]),
                "approvalstate": state,
                "credits": approval_information[2],
                "certifieddate": date.today().strftime("%m/%d/%Y"),
                "clename": name_1,
                "overflow": name_2 if len(name_2) > 0 else "",
            }

            path_to_form = os.path.join(os.getcwd(), "references/certificate_form_empty.pdf")
            reader = PdfReader(path_to_form)
            writer = PdfWriter()
            fields = reader.get_fields()
            writer.append(reader)
            writer.update_page_form_field_values(
                writer.get_page(0), certificate_data, 1
            )

            # write "output" to pypdf-output.pdf
            os.makedirs("output-certificates", exist_ok=True)
            with open(
                "output-certificates/{}-{}-{}.pdf".format(
                    person.name.replace(" ", "_"), state, person.email
                ),
                "wb",
            ) as output_stream:
                writer.write(output_stream)


def round_hours(total_time, state):
    """Round the attended hours according to state guidelines."""
    seconds = total_time.total_seconds()
    if state in ["Missouri"]:
        return "{:.2f}".format((seconds / 3000))
    elif state in ["Indiana"]:
        return "{:.1f}".format((seconds / 3600))
    elif state in ["Pennsylvania"]:
        hours = seconds // 3600
        remainder = (seconds / 60) % 60
        if remainder < 15:
            remainder = 0
        elif 15 <= remainder and remainder < 45:
            remainder = 5
        else:
            remainder = 0
            hours += 1
        return "{:.0f}.{:.0f}".format(hours, remainder)
    elif state in ["Kansas", "Florida"]:
        hours = seconds // 3000
        remainder = (seconds / 60) % 50
        if remainder < 25:
            remainder = 0
        elif 25 <= remainder and remainder < 50:
            remainder = 5
        else:
            remainder = 0
            hours += 1
        return "{:.0f}.{:.0f}".format(hours, remainder)
    else:
        return "{:.2f}".format((seconds / 3600))
