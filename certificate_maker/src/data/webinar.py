from datetime import datetime
import pandas as pd
import csv

from certificate_maker.src.data.attorney import Attorney
from certificate_maker.src.data.cle_class import CleClass


class Webinar:
    """Class to define one webinar event."""

    def __init__(self, zoom_path, cle_master_list_path):
        """Initialize webinar event.

        Args:
            attendees: List[Attorney], list of attorneys that attended
            cle_class: CleClass, the class that was presented at webinar
            event_date: DateTime, date of the webinar
        """
        self.__attendees = []
        self.__cle_class: CleClass = None
        self.__start_time = None
        self.__breaks = []

        self.parse_zoom_data(zoom_path, cle_master_list_path)

    @property
    def attendees(self):
        return self.__attendees

    @attendees.setter
    def attendees(self, attendees):
        self.__attendees = attendees

    @property
    def cle_class(self):
        return self.__cle_class

    @cle_class.setter
    def cle_class(self, cle_class):
        self.__cle_class = cle_class

    @property
    def start_time(self):
        return self.__start_time

    @start_time.setter
    def start_time(self, start_time):
        self.__start_time = start_time

    @property
    def breaks(self):
        return self.__breaks

    @breaks.setter
    def start(self, breaks):
        self.__breaks = breaks

    def add_attendee(self, attorney: Attorney):
        """Add an attendee to attorney list"""
        self.__attendees.append(attorney)

    def get_attendee(self, attorney):
        """Get an attendee given an attorney."""
        for attendee in self.attendees:
            if attorney == attendee:
                return attendee
        return None

    def __build_attendence_roster(self, zoom_data: pd.DataFrame):
        """Return all attorneys in list."""
        zoom_data = zoom_data.reset_index()
        for _, attorney in zoom_data.iterrows():
            new_attorney = Attorney(
                name=attorney["Name"],
                email=attorney["Email"],
                times=[
                    string_to_datetime(attorney["Join Time"]),
                    string_to_datetime(attorney["Leave Time"]),
                ],
                state=attorney["Bar State"],
                bar_number=str(attorney["Bar Number"]),
            )
            if new_attorney in self.__attendees:
                old_attorney = self.get_attendee(new_attorney)
                old_attorney.add_time(
                    [
                        string_to_datetime(attorney["Join Time"]),
                        string_to_datetime(attorney["Leave Time"]),
                    ]
                )
            else:
                self.add_attendee(new_attorney)

    def parse_zoom_data(self, zoom_file_path, cle_master_list_path):
        """Take zoom csv file and get attendence information."""
        rows_to_skip = 0
        check_next_line = False
        with open(zoom_file_path, "r", encoding="utf-8") as zoom_reader:
            reader = csv.reader(zoom_reader, delimiter=",")
            for i, line in enumerate(reader):
                if check_next_line:
                    cle_name = line[0]
                    cle_date = string_to_datetime(line[2]).date()

                    check_next_line = False
                elif len(line) > 0 and line[0] == "Topic":
                    check_next_line = True
                elif len(line) > 0 and line[0] == "Start":
                    self.__start_time = string_to_datetime(line[1])
                elif len(line) > 0 and line[0] == "Breaks":
                    for j in range(2, 2 * int(line[1]) + 1, 2):
                        self.__breaks.append(
                            [
                                string_to_datetime(line[j]),
                                string_to_datetime(line[j + 1]),
                            ]
                        )
                elif len(line) > 0 and line[0] == "Attendee Details":
                    rows_to_skip = i + 1
                    break
        zoom_data = pd.read_csv(
            zoom_file_path, skiprows=rows_to_skip, index_col=False
        )
        zoom_data["Name"] = zoom_data["First Name"] + " " + zoom_data["Last Name"]

        try:
            cut_off = zoom_data.iloc[
                zoom_data[zoom_data["Attended"] == "Other Attended"].index.to_list()[0] :
            ].index.to_list()
            zoom_data.drop(cut_off, inplace=True)
        except:
            pass
        did_not_attend = zoom_data[zoom_data["Attended"] == "No"].index.to_list()
        zoom_data.drop(
            columns=[
                "First Name",
                "Last Name",
                "User Name (Original Name)",
                "Phone",
                "Registration Time",
                "Approval Status",
                "Time in Session (minutes)",
                "Is Guest",
                "Country/Region Name",
            ],
            inplace=True,
        )
        zoom_data.drop(did_not_attend, inplace=True)
        self.__build_attendence_roster(zoom_data)
        for person in self.attendees:
            person.adjust_for_start(self.start_time)
            person.remove_dead_time()
            person.prune_time_list()
            person.adjust_for_breaks(self.breaks)
            person.adjust_for_start(self.start_time)
            person.get_total_time()
            person.remove_dead_time()
            person.parse_bar_numbers()
            person.parse_states()
        
        self.cle_class = CleClass(cle_name, cle_date)
        self.cle_class.get_approvals(cle_master_list_path)


def string_to_datetime(time):
    try:
        time = datetime.strptime(time, "%m/%d/%Y %H:%M")
    except:
        try:
            time = datetime.strptime(time, "%b %d, %Y %I:%M %p")
        except:
            try:
                time = datetime.strptime(time, "%b %d, %Y %H:%M")
            except:
                time = datetime.strptime(time, "%m/%d/%Y %M:%M %p")
    return time.replace(second=0, microsecond=0)
