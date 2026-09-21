from datetime import datetime, timedelta
from certificate_maker.src.data.ref import states_abbrev, states_full, states_dict
import logging

from certificate_maker.src.exception_types import (
    AttorneyInvalidBarNumber,
    AttorneyInvalidState,
)


class Attorney:
    """Class to represent an attorney attending a CLE."""

    def __init__(
        self,
        first_name: str,
        last_name: str,
        email: str,
        times: list[datetime],
        state: list[str],
        bar_number: list[str],
        phone_number: str,
    ) -> None:
        self.__first_name = first_name
        self.__last_name = last_name
        self.__email = email
        self.__phone_number = phone_number
        self.__times = [times]
        self.__states = state
        self.__bar_numbers = bar_number
        self.__total_time = timedelta(hours=0)

    @property
    def name(self) -> str:
        return f"{self.__first_name} {self.__last_name}"

    @property
    def first_name(self) -> str:
        return self.__first_name

    @first_name.setter
    def first_name(self, first_name: str) -> None:
        self.__first_name = first_name

    @property
    def last_name(self) -> str:
        return self.__last_name

    @last_name.setter
    def last_name(self, last_name: str) -> None:
        self.__last_name = last_name

    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, email: str) -> None:
        self.__email = email

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @phone_number.setter
    def phone_number(self, phone_number: str) -> None:
        self.__phone_number = phone_number

    @property
    def times(self) -> list[list[datetime]]:
        return self.__times

    @times.setter
    def times(self, times: list[list[datetime]]) -> None:
        self.__times = times

    @property
    def states(self) -> list[str]:
        return self.__states

    @states.setter
    def states(self, states: list[str]) -> None:
        self.__states = states

    @property
    def bar_numbers(self) -> list[str]:
        return self.__bar_numbers

    @bar_numbers.setter
    def bar_numbers(self, bar_numbers: list[str]) -> None:
        self.__bar_numbers = bar_numbers

    @property
    def total_time(self) -> timedelta:
        return self.__total_time

    @total_time.setter
    def total_time(self, total_time: timedelta) -> None:
        self.__total_time = total_time

    def add_time(self, time: list[datetime]) -> None:
        """Add time to time list."""
        self.__times.append(time)

    def parse_states(self) -> None:
        """Split the states in the state attribute."""
        checked_state_list = []
        for state in self.__states:
            if isinstance(state, str) and (
                state.title().strip() in states_full
                or state.upper().strip() in states_abbrev
            ):
                checked_state_list.append(state)
            else:
                logging.info(
                    f"Check State: `{self.name}` may have two states in one spot."
                )
                if state == "nan":
                    break
                logging.error(
                    f"Check State: `{self.name}` does not have a valid state listed."
                )
                raise AttorneyInvalidState(self.name)
        self.__states = [
            states_dict[x.upper()] if x.upper() in states_abbrev else x.title().strip()
            for x in checked_state_list
        ]

    def parse_bar_numbers(self) -> None:
        """Split the bar numbers into a list."""
        checked_bar_numbers = []
        for number in self.bar_numbers:
            number = number.replace("#", "")
            number = number.replace(".0", "")
            if number.isdigit():
                checked_bar_numbers.append(number.strip())
            elif "-" in number:
                checked_bar_numbers.append(number.strip())
        if not len(checked_bar_numbers):
            logging.error(
                f"Check Bar Number: `{self.name}` does not have a valid bar number listed."
            )
            raise AttorneyInvalidBarNumber(self.name)
        self.bar_numbers = checked_bar_numbers

    def get_total_time(self) -> None:
        """Get total time spent at webinar."""
        for period in self.__times:
            self.__total_time += period[1] - period[0]

    def prune_time_list(self) -> None:
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

    def adjust_for_start(self, start_time: datetime) -> None:
        """Makes sure earliest start times are not before class starts."""
        for index_0, period in enumerate(self.__times):
            for index_1, time in enumerate(period):
                if time is not None and time < start_time:
                    self.__times[index_0][index_1] = start_time

    def adjust_for_breaks(self, breaks: list[list[datetime]]) -> None:
        """Makes sure time is not counted during breaks."""
        for break_period in breaks:
            for index, period in enumerate(self.__times):
                # If time period starts before break and ends during break
                if (
                    period[0] <= break_period[0]
                    and period[1] <= break_period[1]
                    and period[1] >= break_period[0]
                ):
                    self.__times[index][1] = break_period[0]
                # If time period starts during the break
                elif period[0] <= break_period[1] and period[0] >= break_period[0]:
                    self.__times[index][0] = break_period[1]
                # If break is encompassed by the time period
                elif period[0] <= break_period[0] and period[1] >= break_period[1]:
                    self.__times[index] = [period[0], break_period[0]]
                    self.__times.append([break_period[1], period[1]])

    def remove_dead_time(self) -> None:
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
