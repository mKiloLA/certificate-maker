from datetime import datetime
import pandas as pd
import csv
import logging

from certificate_maker.src.data.attorney import Attorney
from certificate_maker.src.data.cle_class import CleClass
from certificate_maker.src.exception_types import (
    IncorrectDateTimeFormat,
    IncorrectNumberOfBreaks,
    IncorrectBreakDate,
    MissingBreakRow,
    MissingStartRow
)


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
                first_name=attorney["First Name"].strip(),
                last_name=attorney["Last Name"].strip(),
                email=attorney["Email"].strip(),
                times=[
                    string_to_datetime(attorney["Join Time"]),
                    string_to_datetime(attorney["Leave Time"]),
                ],
                state=attorney["Bar State"].strip(),
                bar_number=str(attorney["Bar Number"].strip()),
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
        # Rows to skip to get to first attendee. To be set later
        rows_to_skip = 0

        # bool to set when next line contains information
        check_next_line = False
        has_start = False
        has_breaks = False

        # open the zoom file as a reader with a comma delimiter
        with open(zoom_file_path, "r", encoding="utf-8") as zoom_reader:
            reader = csv.reader(zoom_reader, delimiter=",")

            # i is an index and line is an iterable containing one cell of row
            for i, line in enumerate(reader):
                # if check next line is true, then parse data from next row
                if check_next_line:
                    cle_name = line[0]
                    cle_date = string_to_datetime(line[2]).date()
                    check_next_line = False
                # check length to prevent invalid index error
                elif len(line) > 0 and line[0] == "Topic":
                    # topic comes in the row before Webinar title
                    check_next_line = True
                elif len(line) > 0 and line[0] == "Start":
                    # get the start time of webinar
                    has_start = True
                    self.__start_time = string_to_datetime(line[1])
                elif len(line) > 0 and line[0] == "Breaks":
                    has_breaks = True

                    # If no breaks are put in, assume 0 breaks
                    num_of_breaks = int(line[1]) if line[1].isdigit() else 0
                    
                    # get the breaks. line[1] has the number of breaks
                    for j in range(2, 2 * num_of_breaks + 1, 2):
                        # first time is start of break, second is end of break
                        try:
                            break_start = string_to_datetime(line[j])
                            break_end = string_to_datetime(line[j + 1])
                            if not (break_start.date()==cle_date and break_end.date()==cle_date):
                                raise IncorrectBreakDate
                            self.__breaks.append(
                                [
                                    break_start,
                                    break_end
                                ]
                            )
                        except IncorrectDateTimeFormat as e:
                            # if string is empty, then not enough times were given
                            if str(e) == "":
                                raise IncorrectNumberOfBreaks(line[1])
                            # otherwise, just return standard error
                            else:
                                raise IncorrectDateTimeFormat(e)
                        except IncorrectBreakDate:
                            raise IncorrectBreakDate
                # last line before attendee data begins
                elif len(line) > 0 and line[0] == "Attendee Details":
                    # skips the header rows when loading data into df
                    rows_to_skip = i + 1
                    break
        if not has_start:
            raise MissingStartRow
        elif not has_breaks:
            raise MissingBreakRow
        
        # load the file into a df
        zoom_data = pd.read_csv(zoom_file_path, skiprows=rows_to_skip, index_col=False)

        # not sure what this is yet
        try:
            cut_off = zoom_data.iloc[
                zoom_data[zoom_data["Attended"] == "Other Attended"].index.to_list()[
                    0
                ] :
            ].index.to_list()
            zoom_data.drop(cut_off, inplace=True)
        except:
            pass

        # Get all users that signed up but did not attend
        did_not_attend = zoom_data[zoom_data["Attended"] == "No"].index.to_list()

        # drop data columns we do not use
        zoom_data.drop(
            columns=[
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

        # drop the users that signed up and did not attend
        zoom_data.drop(did_not_attend, inplace=True)

        # build attendence roster with zoom data
        self.__build_attendence_roster(zoom_data)

        # for each attendee, calculate their time in class
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

        # create a CLE object and add approvals
        self.cle_class = CleClass(cle_name, cle_date)
        self.cle_class.get_approvals(cle_master_list_path)


def string_to_datetime(time):
    """Given a date as a string, return a datetime object."""
    try:
        time = datetime.strptime(time, "%m/%d/%Y %H:%M")
    except:
        try:
            time = datetime.strptime(time, "%b %d, %Y %I:%M %p")
        except:
            try:
                time = datetime.strptime(time, "%b %d, %Y %H:%M")
            except:
                try:
                    time = datetime.strptime(time, "%m/%d/%Y %H:%M %p")
                except:
                    try:
                        time = datetime.strptime(time, "%m/%d/%Y %I:%M %p")
                    except:
                        try:
                            time = datetime.strptime(time, "%m/%d/%y %H:%M %p")
                        except:
                            try:
                                time = datetime.strptime(time, "%m/%d/%y %H:%M")
                            except:
                                try:
                                    time = datetime.strptime(time, "%b %d, %Y %H:%M:%S")
                                except:
                                    try:
                                        time = datetime.strptime(time, "%b %d, %Y %I:%M:%S")
                                    except:
                                        logging.error(f"Failed to parse time information for `{time}`.")
                                        raise IncorrectDateTimeFormat(time)
    return time.replace(second=0, microsecond=0)
