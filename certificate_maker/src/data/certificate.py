import os
import json
from pypdf import PdfReader, PdfWriter
from certificate_maker.src.data.webinar import Webinar
from datetime import date, timedelta
from typing import Any

from certificate_maker.src.data.ref import us_state_to_abbrev
from certificate_maker.src.exception_types import (
    MismatchingStateAndBarNumbers,
)


def create_certificates(
    zoom_file: str, webinar_file: str, create: bool = True
) -> str | None:
    """Create certificates and serialize attendee data to JSON.

    When ``create`` is false, the input files are validated without writing
    certificates or a JSON output file.
    """
    # Create a webinar object using the provided files
    webinar = Webinar(zoom_file, webinar_file)
    if webinar.cle_class is None:
        raise RuntimeError("Webinar class data was not loaded.")
    cle_class = webinar.cle_class
    max_approved_hours = max(
        float(approval_information[1])
        for approval_information in cle_class.approvals.values()
    )
    date_no_delim = cle_class.cle_date.strftime("%m%d%Y")
    cle_name = cle_class.cle_name

    desired_filename = os.path.join(
        os.path.expanduser("~"),
        f"CertificateMaker/Webinar/{date_no_delim}, {cle_name.replace(':', '-')}/",
    )
    json_filename = os.path.join(
        desired_filename, f"{date_no_delim}, {cle_name.replace(':', '-')}.json"
    )

    if create:
        os.makedirs(desired_filename, exist_ok=True)

    serialization_dict: dict[str, Any] = {
        "desiredpath": desired_filename,
        "datecreated": date.today().strftime("%m/%d/%Y") + ", by CM",
    }
    attendee_list = []

    # Loop through every webinar attendee to make a certificate
    for person in webinar.attendees:
        # Make sure there is one bar number for each state
        if len(person.bar_numbers) != len(person.states):
            raise MismatchingStateAndBarNumbers(person.name)

        # Loop through each state in their profile. Make seperate certificates for each state
        for index, state in enumerate(person.states):
            approval_information = cle_class.approvals.get(state)
            approved = approval_information is not None

            name_1, name_2, name_3 = _split_course_title(cle_class.cle_name)

            # Give grace if the person missed less than 0.1 hours
            rounded_hours = float(round_hours(person.total_time, state))
            if approved:
                total_approved_time = float(approval_information[1])
                if round(abs(rounded_hours - total_approved_time), 2) <= 0.1:
                    rounded_hours = total_approved_time
                attended_hours = min(rounded_hours, total_approved_time)
            else:
                attended_hours = rounded_hours

            # create a dictionary holding all the attendee information
            certificate_data = {
                "name": person.name,
                "state": state,
                "barnumber": f"#{person.bar_numbers[index]}",
                "attendedhours": f"{attended_hours:.2f}",
                "cledate": cle_class.cle_date.strftime("%B %d, %Y"),
                "totalhours": approval_information[1] if approved else "",
                "coursenumber": f"#{approval_information[0]}" if approved else "N/A",
                "approvalstate": state,
                "credits": approval_information[2] if approved else "",
                "certifieddate": date.today().strftime("%m/%d/%Y"),
                "clename": name_1,
                "overflow": " ".join(filter(None, (name_2, name_3))),
                "email": person.email,
                "phonenumber": person.phone_number,
                "approved": approved,
            }

            if create:
                course_title = "\n".join(filter(None, (name_1, name_2, name_3)))
                course_title = f"“{course_title}”"
                hours_text = (
                    f"for {attended_hours:.2f} hours"
                    if approved
                    else _format_attendance_duration(
                        person.total_time, max_approved_hours
                    )
                )
                form_data = {
                    "attendee_name": person.name,
                    "bar_state_number": f"{us_state_to_abbrev[state]} #{person.bar_numbers[index]}",
                    "event_date_hours": (
                        f"Has attended the following live, webinar CLE on:\n"
                        f"{cle_class.cle_date.strftime('%A, %B %d, %Y')} "
                        f"{hours_text}"
                    ),
                    "course_title": course_title,
                    "approved_jurisdiction": _approval_summary(cle_class.approvals),
                    "certified_date": certificate_data["certifieddate"],
                }

                # Write dictionary to pdf form located in users home directory
                path_to_form = os.path.join(
                    os.path.expanduser("~"),
                    f"CertificateMaker/References/certificate_form.pdf",
                )
                reader = PdfReader(path_to_form)
                writer = PdfWriter()
                writer.append(reader)
                writer.update_page_form_field_values(
                    writer.get_page(0), form_data, flatten=True
                )
                writer.remove_annotations(None)

                first_name = person.first_name
                last_name = person.last_name

                # add rows to certificate data for serialization
                certificate_data["desiredname"] = os.path.join(
                    desired_filename,
                    f"{last_name}, {first_name}, {us_state_to_abbrev[state]} #{person.bar_numbers[index]}, COL Certificate of Attendance, {date_no_delim}.pdf",
                )
                attendee_list.append(certificate_data)

                with open(
                    certificate_data["desiredname"],
                    "wb",
                ) as output_stream:
                    writer.write(output_stream)

    if create:
        serialization_dict["attendees"] = attendee_list
        json_object = json.dumps(serialization_dict, indent=4)
        with open(json_filename, "w") as outfile:
            outfile.write(json_object)
        return json_filename


def _split_course_title(title: str, max_line_length: int = 30) -> tuple[str, str, str]:
    lines: list[str] = []
    current_words: list[str] = []
    current_length = 0

    for word in title.split():
        if current_words and current_length + len(word) > max_line_length:
            if len(lines) == 2:
                truncated_line = " ".join(current_words)
                return lines[0], lines[1], f"{truncated_line}..."
            lines.append(" ".join(current_words))
            current_words = []
            current_length = 0

        if len(lines) == 2 and len(word) > max_line_length:
            return lines[0], lines[1], f"{word[:max_line_length - 3]}..."

        current_words.append(word)
        current_length += len(word)

    if current_words:
        lines.append(" ".join(current_words))
    lines.extend([""] * (3 - len(lines)))
    return lines[0], lines[1], lines[2]


def _format_attendance_duration(duration: timedelta, max_hours: float) -> str:
    """Round attended time up by 15 minutes without exceeding approved hours."""
    interval_seconds = 15 * 60
    total_seconds = int(duration.total_seconds())
    rounded_seconds = (
        (total_seconds + interval_seconds - 1) // interval_seconds
    ) * interval_seconds
    hours = min(rounded_seconds / (60 * 60), max_hours)
    return f"for {hours:.2f} hours"


def _approval_summary(approvals: dict[str, list[Any]]) -> str:
    """Format approved jurisdictions using the certificate's credit legend."""
    summaries = []
    credit_codes = ("EOB", "SAC", "DV", "IB", "SA", "C", "D", "E", "G", "P")

    for state, approval in approvals.items():
        course_number, total_hours, credits = approval
        normalized_course_number = (
            "" if course_number is None else str(course_number).strip()
        )
        if normalized_course_number.upper() == "N/A":
            continue

        state_abbreviation = us_state_to_abbrev[state]
        course_text = (
            "no course number"
            if normalized_course_number.casefold() in {"", "none"}
            else f"course #{normalized_course_number}"
        )
        summary = f"{state_abbreviation}, {course_text}, {total_hours} total hours"
        if credits:
            credit_text = []
            for credit in str(credits).split(", "):
                credit = credit.strip()
                code = next(
                    (
                        known_code
                        for known_code in credit_codes
                        if credit.upper().endswith(known_code)
                    ),
                    credit[-1:].upper(),
                )
                amount = credit[: -len(code)]
                credit_text.append(
                    f"{amount} {code} "
                    f"{'hour' if amount.strip() in {'1', '1.0'} else 'hours'}"
                )
            summary += f", including {', '.join(credit_text)}"
        summaries.append(summary)

    return "\n".join(summaries)


def round_hours(total_time: Any, state: str) -> str:
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
