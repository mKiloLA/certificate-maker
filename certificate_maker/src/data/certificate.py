import os
import json
from pypdf import PdfReader, PdfWriter
from certificate_maker.src.data.webinar import Webinar
import logging
from datetime import date

from certificate_maker.src.data.ref import states_dict, us_state_to_abbrev
from certificate_maker.src.exception_types import MissingStateApproval, MismatchingStateAndBarNumbers


def create_certificates(zoom_file, webinar_file, create=True):
    # Create a webinar object using the provided files
    webinar = Webinar(zoom_file, webinar_file)
    date_no_delim = webinar.cle_class.cle_date.strftime("%m%d%Y")
    cle_name = webinar.cle_class.cle_name

    output_filename = os.path.join(os.path.expanduser('~'), f"Certificates/Output/{date_no_delim} {cle_name.replace(':', '')}/")
    desired_filename = os.path.join(os.path.expanduser('~'), f"Certificates/Output/{date_no_delim}, {cle_name.replace(':', '-')}/")
    json_filename = os.path.join(output_filename, f"{date_no_delim}, {cle_name.replace(':', '-')}.json")

    if create:
        os.makedirs(output_filename, exist_ok=True)
        os.makedirs(desired_filename, exist_ok=True)

    serialization_dict = {
        "filepath": output_filename,
        "desiredpath": desired_filename
    }
    attendee_list = []

    # Loop through every webinar attendee to make a certificate
    for person in webinar.attendees:

        # Make sure there is one bar number for each state
        if len(person.bar_numbers) != len(person.states):
            raise MismatchingStateAndBarNumbers(person.name)
        
        # Loop through each state in their profile. Make seperate certificates for each state
        for index, state in enumerate(person.states):
            # Check if the class is approved in that state, if not throw error
            try:
                approval_information = webinar.cle_class.approvals[state]
            except:
                logging.error(f"Check State Approvals: `{person.name}` has no approval infomation in the state of `{state}`.")
                raise MissingStateApproval((person.name, state))
            
            # Split the class name by spaces and then check lengths. This is to prevent overflow on pdf
            og_name_list = webinar.cle_class.cle_name.split(" ")
            first_name_list = []
            overflow_name_list = []
            total_length = 0
            for name in og_name_list:
                if total_length + len(name) >= 30:
                    overflow_name_list.append(name)
                    total_length += len(name)
                else:
                    first_name_list.append(name)
                    total_length += len(name)
            name_1 = " ".join(first_name_list)
            name_2 = " ".join(overflow_name_list)

            rounded_hours = float(round_hours(person.total_time, state))
            total_approved_time = float(approval_information[1])
            print(f"Rounded: {rounded_hours}, Approved: {total_approved_time}")

            # create a dictionary holding all the attendee information
            certificate_data = {
                "name": person.name,
                "state": state,
                "barnumber": f"#{person.bar_numbers[index]}",
                "attendedhours": f"{float(round_hours(person.total_time, state)) if float(round_hours(person.total_time, state)) < float(approval_information[1]) else float(approval_information[1]):.2f}",
                "cledate": webinar.cle_class.cle_date.strftime("%B %d, %Y"),
                "totalhours": approval_information[1],
                "coursenumber": f"#{approval_information[0]}",
                "approvalstate": state,
                "credits": approval_information[2],
                "certifieddate": date.today().strftime("%m/%d/%Y"),
                "clename": name_1,
                "overflow": name_2 if len(name_2) > 0 else "",
                "email": person.email
            }

            if create:
                # Write dictionary to pdf form located in users home directory
                path_to_form = os.path.join(os.path.expanduser('~'), "Certificates/References/certificate_form_empty.pdf")
                reader = PdfReader(path_to_form)
                writer = PdfWriter()
                fields = reader.get_fields()
                writer.append(reader)
                writer.update_page_form_field_values(
                    writer.get_page(0), certificate_data, 1
                )

                first_name = person.first_name
                last_name = person.last_name

                # add rows to certificate data for serialization
                certificate_data["filename"] = os.path.join(desired_filename, f"{last_name} {first_name} {person.bar_numbers[index]}.pdf")
                certificate_data["desiredname"] = os.path.join(desired_filename, f"{last_name}, {first_name}, {us_state_to_abbrev[state]} #{person.bar_numbers[index]}, COL Certificate of Attendance, {date_no_delim}.pdf")
                attendee_list.append(certificate_data)

                with open(
                    os.path.join(output_filename, f"{last_name} {first_name} {person.bar_numbers[index]}.pdf"),
                    "wb",
                ) as output_stream:
                    writer.write(output_stream)

    if create:
        serialization_dict["attendees"] = attendee_list
        json_object = json.dumps(serialization_dict, indent=4)
        with open(json_filename, "w") as outfile:
            outfile.write(json_object)
        return json_filename

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
