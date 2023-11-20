class IncorrectWebinarTitle(Exception):
    pass

class IncorrectDateTimeFormat(Exception):
    pass

class IncorrectNumberOfBreaks(Exception):
    pass

class MasterListMissingHours(Exception):
    pass

class MissingStateApproval(Exception):
    pass

class AttorneyMissingState(Exception):
    pass

class AttorneyMissingBarNumber(Exception):
    pass

class AttorneyInvalidState(Exception):
    pass

class AttorneyInvalidBarNumber(Exception):
    pass

class MissingStartRow(Exception):
    pass

class MissingBreakRow(Exception):
    pass

class MismatchingStateAndBarNumbers(Exception):
    pass

class IncorrectBreakDate(Exception):
    pass
