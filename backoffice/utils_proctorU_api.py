from collections import defaultdict
import datetime
import dateutil
import json
import logging
import sys

import requests

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from .certificate_manager.verified import get_enrolled_verified_students
from .utils import get_course_key


logger = logging.getLogger(__name__)

def is_in_prod():
    """
    Utility function to tell in we are in test, dev or preprod/prod settings.
    We don't query the users the same way according the setup.

    :return: boolean are we in preprod/prod or not
    """
    try:
        settings.TEST_ROOT  # are we in test mode ?
    except AttributeError:
        test = False
    else:
        test = True

    if test:
        return False  # if we are in test, we are not in prod

    return not settings.DEBUG  # if we are in debug mode, we are not in prod

def format_date(date_str):
    return dateutil.parser.parse(date_str).strftime(_('%m/%d/%y %H:%M'))


class API(object):

    def __init__(self, course_name, course_run, student_grades = None, base_url=None, token=None):
        self.endpoints = {
            "get_time_zone": "/api/getTimeZoneList",
            "get_sche_info_avl_time_list": "/api/getScheduleInfoAvailableTimesList",
            "add_adhoc_process": "/api/addAdHocProcess",
            "remove_reservation": "/api/removeReservation",
            "client_activity_report": "/api/clientActivityReport",
            "student_reservation_list": "/api/getStudentReservationList",
            "begin_reservation": "/api/beginReservation",
            "edit_student": "/api/editStudent",
        }

        self.base_url = base_url if base_url else "https://" + settings.PROCTORU_API
        self.header = {"Authorization-Token": token if token else settings.PROCTORU_TOKEN}
        self.in_prod = is_in_prod()
        self.api_request_data()

        self.course_name = course_name
        self.course_run = course_run
        self.student_grades = student_grades

    def query_api(self, request_method, url):
        self.request_data["time_sent"] = datetime.datetime.utcnow().isoformat()

        try:
            resp = request_method(url, data=self.request_data, headers=self.header)
            student_activity = resp.content
        except requests.ConnectionError as e:
            logger.exception(e)
            return {"error": "Connection error while connecting to {}".format(url)}
        except requests.exceptions.SSLError as e:
            logger.exception(e)
            return {"error": "SSL error while connecting to {}".format(url)}

        if resp.status_code == 500:
            mess = "Error 500 in proctorU api for url : {}".format(url)
            logger.error(mess)
            return {"error": mess}

        student_activity_json = json.loads(student_activity)
        if student_activity_json["response_code"] != 1:
            if student_activity_json["message"] == "stale request":
                logger.error("Error in ProctorU API configuration, received : stale request")
                return {"error": student_activity_json["message"]}
            else:
                logger.error("ProctorU API error, message : {}".format(student_activity_json["message"]))
                return {"error": student_activity_json["message"]}

        return student_activity_json

    def extract_infos(self, report):
        tmp = {
            "Student": report["Student"],
            "ProctorNotes": report["ProctorNotes"],
            "UniqueId": report["UniqueId"],
            "ReservationNo": report["ReservationNo"],
            "TestSubmitted": report["Authenticated"],
            "CheckID": report["CheckID"],
            "StartDate": format_date(report["StartDate"]),
            "Authenticated": report["Authenticated"],
            "IncidentReport": report["IncidentReport"],
            "Escalated": report["Escalated"],
            "fun_user_url": None,
            "fun_exam_grade": None,
            "fun_exam_pass": None,
        }
        return tmp

    def get_proctoru_students(self):
        url = self.base_url + self.endpoints["client_activity_report"]
        student_activity = self.query_api(requests.post, url)
        if "error" in student_activity:
            return student_activity

        filtered_reports = self.filter_reports_for_course(student_activity)
        if "error" in filtered_reports or "warn" in filtered_reports:
            return filtered_reports

        return self.aggregate_reports_per_user(filtered_reports)

    def aggregate_reports_per_user(self, filtered_reports):
        """
        Aggregate the lines present in the API according the user.
        The API returns a line for each events, but we are really interested in the "profile" for each user.

        ProctorU API seems bugged, it contains duplicated lines (usually consecutive), so we also remove the consecutive
        duplicates.

        :param filtered_reports: iterable with the ProctorU reports filtered with the course of interest
        :param student_grades: dictionary with the student username as key and info about their exam grade in values
        :return: dict with the fun username as key and the list of "actions" / reports for this user
        """
        filtered_reports.sort(key=lambda d: d["Student"])

        first_report = filtered_reports[0]
        id_ = int(first_report["UniqueId"])
        identifiers = [id_]
        event_users = defaultdict(list)
        event_users[id_].append(self.extract_infos(first_report))

        prec_json = filtered_reports[0]
        for report in filtered_reports[1:]:
            tmp = self.extract_infos(report)
            if report != prec_json:
                event_users[int(report["UniqueId"])].append(tmp)
                identifiers.append(int(report["UniqueId"]))
            prec_json = report

        event_users = dict(event_users)
        if not is_in_prod():
            fun_users = User.objects.filter(last_name__in=identifiers)
        else:
            fun_users = User.objects.filter(id__in=identifiers)

        res = {}
        for user in fun_users:
            if not is_in_prod():
                id_ = int(user.last_name)  # Ugly! : in dev we added the production primary key in the filed last name
            else:
                id_ = user.id

            url = reverse("backoffice:user-detail", args=[user.username])
            event_users[id_][0]["fun_user_url"] = url

            if self.student_grades:
                try:
                    grade = self.student_grades[user.username]["grade"]
                    passed = self.student_grades[user.username]["passed"]
                except KeyError:
                    mess = "User {} is not in student_grades".format(user.username)
                    logger.info(mess)
                else:
                    event_users[id_][0]["fun_exam_grade"] = grade
                    event_users[id_][0]["fun_exam_pass"] = passed
            event_users[id_][0]["user"] = user
            res[user.username] = event_users[id_]

        return res

    def filter_reports_for_course(self, student_activity):
        """
        Only keep the course of interest from the API query.
        This should be done API side, but it is not possible for the moment :(

        :param student_activity: dict with the API response
        :return: dict with the API response about the course
        """
        proctoru_test_id = "{} {}".format(self.course_name, self.course_run)

        reports = student_activity["data"]
        if not reports:
            mess = "Empty response from the API"
            logger.info(mess)
            return {"error": mess}
        filtered_reports = [report for report in reports if proctoru_test_id in report["Test"]]
        if not filtered_reports:
            mess = "No student for course {} between {} and {}".format(proctoru_test_id,
                                                                       self.request_data["start_date"],
                                                                       self.request_data["end_date"])
            logger.info(mess)
            return {"warn": {"id": proctoru_test_id,
                             "start": format_date(self.request_data["start_date"]),
                             "end": format_date(self.request_data["end_date"])}}
        return filtered_reports

    def api_request_data(self):
        start = datetime.datetime.today() - datetime.timedelta(days=100)
        end = datetime.datetime.today() + datetime.timedelta(days=100)
        start_date = start.isoformat()
        end_date = end.isoformat()
        self.request_data = {
            "end_date": end_date,
            "start_date": start_date,
        }

def get_verified_students_without_proctoru_reservations(course_key_string, proctoru_base=False, proctoru_token=False):
        course_key = get_course_key(course_key_string)
        verified_students = get_enrolled_verified_students(course_key)

        proctoru_API = API(course_name=course_key.course, course_run=course_key.run,
                           base_url=proctoru_base, token=proctoru_token)
        proctoru_reports = proctoru_API.get_proctoru_students()
        if "warn" in proctoru_reports:
            sys.exit("ProctorU is empty for this course, is everything OK?")
        if "error" in proctoru_reports:
            sys.exit(proctoru_reports["error"])
        proctoru_users = [reports[0]["user"] for reports in proctoru_reports]
        print(proctoru_users, verified_students)
        enrolled_students_not_proctoru = set(verified_students) - set(proctoru_users)
        return enrolled_students_not_proctoru
