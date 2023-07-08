from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()

# writer.append(reader)
# information = {
#     'Text1': 'ONE\nFIVE',
#     'Text2': 'TWO',
#     'Text3': 'THREE',
#     'Text4': 'FOUR'
# }
# writer.update_page_form_field_values(
#     writer.pages[0], information, 1
# )

# # write "output" to pypdf-output.pdf
# with open("filled-out.pdf", "wb") as output_stream:
#     writer.write(output_stream)
from .webinar import Webinar
from datetime import datetime
import re

if __name__ == "__main__":
    webinar = Webinar("references\zoom_attendence.csv", "references\master_webinar_list.xlsx")
    for person in webinar.attendees:
        print("{}: {} - {} - {}".format(person.name, person.total_time, person.states, person.bar_numbers))
        reader = PdfReader("certificate_form.pdf")
        writer = PdfWriter()
        # page = reader.pages[0]
        # print(page)
        # fields = reader.get_fields()
        # print(fields)