from openpyxl import load_workbook
from certificate_maker.src.data.ref import states_dict, new_york_approvals

class CleClass:
    """Class to represent one class that an attorney can attend."""

    def __init__(self, cle_name, cle_date):
        self.__cle_name = cle_name
        self.__cle_date = cle_date
        self.__approvals = {}

    @property
    def cle_name(self):
        return self.__cle_name

    @cle_name.setter
    def cle_name(self, cle_name):
        self.__cle_name = cle_name

    @property
    def cle_date(self):
        return self.__cle_date

    @cle_date.setter
    def cle_date(self, cle_date):
        self.__cle_date = cle_date

    @property
    def approvals(self):
        return self.__approvals

    @approvals.setter
    def approvals(self, approvals):
        self.__approvals = approvals

    def get_approvals(self, cle_master_list_path):
        """Get all approved instances of the class."""
        wb = load_workbook(filename = cle_master_list_path)
        for sheet in wb:
            for row in sheet.values:
                if row[2] == self.cle_name and row[3].date() == self.cle_date:
                    self.approvals[states_dict[sheet.title[0:2]]] = [row[6], row[9]]
        self.__approved_jurisdictions()
        self.__parse_credit_type()

    def __approved_jurisdictions(self):
        """Add states that are approved because of other approved states."""
        for key in self.approvals:
            if key in new_york_approvals:
                break
        self.approvals["New York"] = ["N/A", self.approvals[key][1]]
        self.approvals["New Jersey"] = ["N/A", self.approvals[key][1]]

    def __parse_credit_type(self):
        """Split the types of credit into readable format."""
        print(self.approvals)
        for key in self.approvals:
            total_hours = 0
            parsed_credits = []
            if self.approvals[key][1] is not None:
                credit_list = self.approvals[key][1].split("/")
            course_number = self.approvals[key][0]
            for index, hour in enumerate(credit_list):
                if "T" in hour:
                    total_hours = hour[:-1]
                elif "SAC" in hour:
                    parsed_credits.append("{}h substance abuse and competency".format(hour[:-3]))
                elif "EOB" in hour:
                    parsed_credits.append("{}h elimination of bias".format(hour[:-3]))
                elif "SA" in hour:
                    parsed_credits.append("{}h substance abuse".format(hour[:-2]))
                elif "E" in hour:
                    parsed_credits.append("{}h ethics".format(hour[:-1]))
                elif "G" in hour:
                    parsed_credits.append("{}h general".format(hour[:-1]))
                elif "D" in hour:
                    parsed_credits.append("{}h diversity".format(hour[:-1]))
                elif "C" in hour:
                    parsed_credits.append("{}h competency".format(hour[:-1]))
                elif "P" in hour:
                    parsed_credits.append("{}h professionalism".format(hour[:-1]))
                else:
                    parsed_credits.append("Not approved for credit.")
            self.approvals[key] = [course_number, total_hours, ", ".join(parsed_credits)]
