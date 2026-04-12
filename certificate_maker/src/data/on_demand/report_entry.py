from pandas import Timestamp


class ReportEntry:
    """Class to represent an an entry on the On-Demand Report."""

    def __init__(self, first_name, last_name, email, state, bar_number, course_title, course_completed_date):
        # Obtained from the Attendance file
        self.__first_name : str = first_name
        self.__last_name : str = last_name
        self.__email : str = email
        self.__state : str = state
        self.__bar_number : str = bar_number
        self.__course_title : str = course_title
        self.__course_completed_date : Timestamp = course_completed_date

        # Obtained from the Evaluation file
        self.__course_evaluation : str | None = None
        
        # Found by comparing the on-demand reference file to the attendance and evaluation files
        self.__course_id : str | None = None
        self.__course_hours : str | None = None
        self.__course_expired : bool = False

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
    def state(self):
        return self.__state

    @state.setter
    def state(self, state):
        self.__state = state

    @property
    def bar_number(self):
        return self.__bar_number

    @bar_number.setter
    def bar_number(self, bar_number):
        self.__bar_number = bar_number

    @property
    def course_title(self):
        return self.__course_title

    @course_title.setter
    def course_title(self, course_title):
        self.__course_title = course_title
        return self.__email

    @property
    def course_completed_date(self):
        return self.__course_completed_date

    @course_completed_date.setter
    def course_completed_date(self, course_completed_date):
        self.__course_completed_date = course_completed_date

    @property
    def course_evaluation(self):
        return self.__course_evaluation

    @course_evaluation.setter
    def course_evaluation(self, course_evaluation):
        self.__course_evaluation = course_evaluation

    @property
    def course_id(self):
        return self.__course_id

    @course_id.setter
    def course_id(self, course_id):
        self.__course_id = course_id

    @property
    def course_hours(self):
        return self.__course_hours

    @course_hours.setter
    def course_hours(self, course_hours):
        self.__course_hours = course_hours

    @property
    def course_expired(self):
        return self.__course_expired

    @course_expired.setter
    def course_expired(self, course_expired):
        self.__course_expired = course_expired
