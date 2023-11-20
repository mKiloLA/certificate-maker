from datetime import timedelta
from certificate_maker.src.data.ref import states_abbrev, states_full, states_dict
import re
import logging

from certificate_maker.src.exception_types import (
    AttorneyMissingBarNumber,
    AttorneyMissingState,
    AttorneyInvalidBarNumber,
    AttorneyInvalidState
)


class Attorney:
    """Class to represent an attorney attending a CLE."""

    def __init__(self, first_name, last_name, email, times, state, bar_number):
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__times = [times]
        self.__states = state
        self.__bar_numbers = bar_number
        self.__total_time = timedelta(hours=0)

    @property
    def name(self):
        return f"{self.__first_name} {self.__last_name}"

    @property
    def first_name(self):
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name):
        self.__first_name = first_name

    @property
    def last_name(self):
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name):
        self.__last_name = last_name

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, email):
        self.__email = email

    @property
    def times(self):
        return self.__times

    @times.setter
    def times(self, times):
        self.__times = times

    @property
    def states(self):
        return self.__states

    @states.setter
    def states(self, states):
        self.__states = states

    @property
    def bar_numbers(self):
        return self.__bar_numbers

    @bar_numbers.setter
    def bar_numbers(self, bar_numbers):
        self.__bar_numbers = bar_numbers

    @property
    def total_time(self):
        return self.__total_time

    @total_time.setter
    def total_time(self, total_time):
        self.__total_time = total_time

    def add_time(self, time):
        """Add time to time list."""
        self.__times.append(time)

    def parse_states(self):
        """Split the states in the state attribute."""
        if (
            isinstance(self.__states, str) and 
            (self.__states.title().strip() in states_full
            or self.__states.upper().strip() in states_abbrev)
        ):
            split_states = [self.__states]
        else:
            logging.info(f"Check State: `{self.name}` may have multiple states.")
            if isinstance(self.__states, float):
                logging.error(f"Check State: `{self.name}` has no state listed.")
                raise AttorneyMissingState(self.name)
            if "," in self.__states:
                split_states = [x.strip() for x in self.__states.split(",")]
            elif "&" in self.__states:
                split_states = [x.strip() for x in self.__states.split("&")]
            elif ";" in self.__states:
                split_states = [x.strip() for x in self.__states.split(";")]
            elif "and" in self.__states:
                split_states = [x.strip() for x in self.__states.split("and")]
            elif "/" in self.__states:
                split_states = [x.strip() for x in self.__states.split("/")]
            else:
                logging.error(f"Check State: `{self.name}` does not have a valid state listed.")
                raise AttorneyInvalidState(self.name)
        self.__states = [
            states_dict[x.upper()]
            if x.upper() in states_abbrev
            else x.title().strip()
            for x in split_states
        ]

    def parse_bar_numbers(self):
        """Split the bar numbers into a list."""
        self.__bar_numbers = self.__bar_numbers.replace("#", "")
        self.__bar_numbers = self.__bar_numbers.replace(".0", "")
        if self.__bar_numbers.isdigit():
            self.__bar_numbers = [self.__bar_numbers.strip()]
            return
        elif len(self.__bar_numbers) > 0 and self.__bar_numbers != "nan":
            logging.info("Check Bar Number: `{}` has multiple bar numbers.".format(self.name))
            split_bar_numbers = [x.strip() for x in re.split(", |,| |&|;|and|/", self.__bar_numbers)]
        else:
            logging.error(f"Check Bar Number: `{self.name}` has no bar number listed.")
            raise AttorneyMissingBarNumber(self.name)
        temp = []
        for entry in split_bar_numbers:
            if entry.isdigit():
                temp.append(entry.strip())
            elif "-" in entry:
                temp.append(entry.strip())
        if len(temp) < 1:
            logging.error(f"Check Bar Number: `{self.name}` does not have a valid bar number listed.")
            raise AttorneyInvalidBarNumber(self.name)
        self.bar_numbers = temp

    def get_total_time(self):
        """Get total time spent at webinar."""
        for period in self.__times:
            self.__total_time += period[1] - period[0]

    def prune_time_list(self):
        # if start time is after and end time is after, move on to the next one
        # check if next time started before end of previous and ended after
        # check that next item is not inside of previous item
        for _ in range(12):
            remove_list = []
            keep_list = []
            if len((self.__times)) == 0:
                break
            keep_list.append(self.__times[0])

            for index, time_event in enumerate(self.__times):
                start_time = time_event[0]
                end_time = time_event[1]
                double_break = False

                for _, next_event in enumerate(self.__times):
                    if [start_time, end_time] == next_event:
                        continue
                    elif next_event[1] <= end_time and next_event[0] >= start_time:
                        remove_list.append(next_event)
                        continue
                    elif next_event[0] == start_time:
                        if next_event[1] > end_time:
                            remove_list.append(time_event)
                            keep_list.append(next_event)
                        else:
                            remove_list.append(next_event)
                        continue
                    elif (
                        next_event[1] > end_time
                        and next_event[0] - timedelta(minutes=1) <= end_time
                    ):
                        keep_list.append([start_time, next_event[1]])
                        remove_list.append(next_event)
                        remove_list.append(self.__times[index])
                        double_break = True
                        break
                    elif next_event[0] > end_time:
                        if next_event not in keep_list:
                            keep_list.append(next_event)
                        continue
                if double_break:
                    keep_list.extend(self.__times)
                    break
                elif len(keep_list) == 1 and len(keep_list) + len(remove_list) == len(
                    self.__times
                ):
                    break
            self.__times = [x for x in keep_list if x not in remove_list]
        self.__times = [[x[0], x[1]] for x in self.__times]

    def adjust_for_start(self, start_time):
        """Makes sure earliest start times are not before class starts."""
        for index_0, period in enumerate(self.__times):
            for index_1, time in enumerate(period):
                if time is not None and time < start_time:
                    self.__times[index_0][index_1] = start_time

    def adjust_for_breaks(self, breaks):
        """Makes sure time is not counted during breaks."""
        for break_period in breaks:
            for index, period in enumerate(self.__times):
                if (
                    period[0] < break_period[0]
                    and period[1] < break_period[1]
                    and period[1] > break_period[0]
                ):
                    self.__times[index][1] = break_period[0]
                elif period[0] < break_period[1] and period[0] > break_period[0]:
                    self.__times[index][0] = break_period[1]
                elif period[0] < break_period[0] and period[1] > break_period[1]:
                    self.__times[index] = [period[0], break_period[0]]
                    self.__times.append([break_period[1], period[1]])

    def remove_dead_time(self):
        """Remove time intervals that are empty."""
        for period in self.__times:
            if period[1] - period[0] < timedelta(minutes=1):
                self.__times.remove(period)

    def __eq__(self, __o: object) -> bool:
        """Instances are equal if the name is the same."""
        if isinstance(__o, Attorney):
            if self.name == __o.name:
                return True
            else:
                return False
        else:
            return False
