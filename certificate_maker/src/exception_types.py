"""Application exceptions grouped by the data module that raises them."""


# certificate_maker/src/data/attorney.py
class AttorneyMissingState(Exception):
    pass


class AttorneyInvalidState(Exception):
    pass


class AttorneyMissingBarNumber(Exception):
    pass


class AttorneyInvalidBarNumber(Exception):
    pass


# certificate_maker/src/data/cle_class.py
class IncorrectWebinarTitle(Exception):
    pass


class MasterListMissingHours(Exception):
    pass


# certificate_maker/src/data/webinar.py
class IncorrectDateTimeFormat(Exception):
    pass


class IncorrectNumberOfBreaks(Exception):
    pass


class IncorrectBreakDate(Exception):
    pass


class MissingStartRow(Exception):
    pass


class MissingBreakRow(Exception):
    pass


# certificate_maker/src/data/certificate.py
class MissingStateApproval(Exception):
    pass


class MismatchingStateAndBarNumbers(Exception):
    pass


# certificate_maker/src/data/on_demand/on_demand.py
class MissingSubmissionData(Exception):
    pass


class MissingEvaluationData(Exception):
    pass


class MalformedCROString(Exception):
    pass


class MalformedEvaluationQuestionResponse(Exception):
    pass


class ReferenceFileMissingSheet(Exception):
    pass


class ReferenceFileMissingCourse(Exception):
    pass


# certificate_maker/src/data/state_submission.py
class StateSubmissionFileNotFound(Exception):
    pass


class StateSubmissionInvalidJson(Exception):
    pass


class StateSubmissionMissingData(Exception):
    pass


class StateSubmissionMissingPollData(Exception):
    pass


class StateSubmissionMissingSurveyData(Exception):
    pass
