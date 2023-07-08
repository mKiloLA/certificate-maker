from openpyxl import load_workbook

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
                    self.approvals[sheet.title[0:2]] = [row[6], row[9]]
