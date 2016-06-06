import os


def is_proctoru_ok(proctoru_student_reports):
    """Check ProctorU accept conditions from the reports

    As a debug feature, this function will return True for all students when
    the PROCTORU_ALL_STUDENTS_OK environment variable is defined. This is a
    temporary measure that should be removed when we don't need it anymore.
    (i.e: when we have found a way to abstract ourselves from the ProctorU API)
    """
    if os.environ.get("PROCTORU_ALL_STUDENTS_OK"):
        return True

    if len(proctoru_student_reports) > 0:
        first_report = proctoru_student_reports[0]
        return (
            first_report.get("Authenticated") and
            first_report.get("TestSubmitted") and
            not first_report["Escalated"] and
            not first_report.get("IncidentReport")
        )
    else:
        return False
