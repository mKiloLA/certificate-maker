import os
from pypdf import PdfReader
import smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class AttorneyEmail:
    def __init__(self, name, state, email, clename, cledate):
        self.name = name
        self.state = state
        self.email = email
        self.clename = clename
        self.cledate = cledate

def send_emails(foldername, demo=True):
    files_in_folder = [x for x in os.listdir(foldername) if x.endswith(".pdf")]
    file_locations = [os.path.join(foldername, x) for x in files_in_folder ]

    with open(os.path.join(os.path.expanduser('~'), "Certificates/References/Outlook.txt"), "r") as reader:
        sender_email = reader.readline().strip()
        password = reader.readline().strip()

    context = ssl.create_default_context()
    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls(context=context)
        server.login(sender_email, password)

        for certificate in file_locations:
            filename = certificate
            reader = PdfReader(filename)
            fields = reader.get_form_text_fields()

            person = AttorneyEmail(
                name=fields["name"],
                state=fields["state"],
                email=fields["email"],
                clename=' '.join([fields['clename'], fields['overflow']]),
                cledate=fields["cledate"]
            )

            body = make_body(person)
            if demo:
                receiver_email = sender_email
            else:
                receiver_email = person.email

            # Create a multipart message and set headers
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = receiver_email
            message["Subject"] = f"{person.clename}, {person.state}, {person.cledate}"

            # Add body to email
            message.attach(MIMEText(body, "plain"))

            # Open PDF file in binary mode
            with open(filename, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={person.name} Certificate of Attendance.pdf",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
            text = message.as_string()
            server.sendmail(sender_email, receiver_email, text)

def make_body(attorney):
    bar_statement = ""
    match attorney.state:
        case "Arkansas":
            bar_statement = "I have submitted your attendance to the AR State Bar Association, so it should show up in your account soon."
        case "California":
            bar_statement = "I have submitted your attendance to the CA State Bar Association, so it should show up in your account soon."
        case "Georgia":
            bar_statement = "I have submitted your attendance to the State Bar of GA, so it should show up in your account soon."
        case "Indiana":
            bar_statement = "I have submitted your attendance to the IN State Bar Association, so it should show up in your account soon."
        case "Louisiana":
            bar_statement = "I have submitted your attendance to the LA State Bar Association, so it should show up in your account soon."
        case "Mississippi":
            bar_statement = "I have submitted your attendance to the MS State Bar Association, so it should show up in your account soon."
        case "South Carolina":
            bar_statement = "I have submitted your attendance to the SC CLE Commission, so it should show up in your account soon."
        case "Kansas":
            bar_statement = "I have submitted your attendance to the KS CLE Commission, so it should show up in your account soon."
        case "Iowa":
            bar_statement = "Since IA is a self-reporting state, you will submit your own attendance to the IA State Bar."
        case "Florida":
            bar_statement = "Since FL is a self-reporting state, you will submit your own attendance to the FL Bar."
        case "Missouri":
            bar_statement = "Since MO is a self-reporting state, you will submit your own attendance to The MO Bar."
        case "New Mexico":
            bar_statement = "I have submitted your attendance to NM State Bar Association and paid the attendance fee, so it should show up in your account soon."
        case "North Carolina":
            bar_statement = "I have submitted your attendance to NC State Bar Association and paid the attendance fee, so it should show up in your account soon."
        case "Pennsylvania":
            bar_statement = "I have submitted your attendance to PACLE and paid the attendance fee, so it should show up in your account soon."
        case "Tennessee":
            bar_statement = "I have submitted your attendance to TN CLE Commission and paid the attendance fee, so it should show up in your account soon."
        case "Utah":
            bar_statement = "I have submitted your attendance to Utah State Bar Association and paid the attendance fee, so it should show up in your account soon."
        case "New Jersey":
            bar_statement = f"This CLE qualifies for credit in {attorney.state} through reciprocity. For more information on reciprocity in {attorney.state}, see https://www.njcourts.gov/attorneys/cle/faq#500171."
        case "New York":
            bar_statement = f"This CLE qualifies for credit in {attorney.state} through reciprocity. For more information on reciprocity in {attorney.state}, see https://ww2.nycourts.gov/attorneys/cle/approvedjurisdictions.shtml."
        case "Kentucky":
            bar_statement = ""
        case _:
            bar_statement = ""
    body = f"""
{attorney.name},

Thank you for attending our recent webinar, we do hope you enjoyed it.

I have attached a COL certificate of attendance to this email, which you can keep for your records. {bar_statement}

If you have any questions or concerns, please let me know. Thank you and have a great day!!

Sincerely,
Wendi M. Oster
Comedian of Law LLC
Vice President of Operations
22052 W. 66th St., #192
Shawnee, KS 66226
913-213-9823 – office
info@comedianoflaw.com
www.comedianoflaw.com
Facebook:  https://www.facebook.com/comedianoflaw/
YouTube:  https://www.youtube.com/channel/UChuPFkcuMje22bujQlpgMWg
\n\n"""
    return body
