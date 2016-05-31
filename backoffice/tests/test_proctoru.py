# -*- coding: utf-8 -*-

from collections import namedtuple
import datetime
import json
import os

from mock import patch, Mock

from student.tests.factories import UserFactory

from .. import utils_proctorU_api

from .test import BaseTestCase
from .test_course_list import VerifiedCourseList


def proctorU_api_result(test_key):
    path = os.path.dirname(__file__)
    json_path = os.path.join(path, "proctoru_data.json")
    obj = json.loads(open(json_path).read())
    return obj[test_key]

def simulate_procotru_multiple_resp(first_resps):
    """
    Emulate the pagnation in proctoru API. To keep tings simple, we don't react to the date but send the responses
    written in the json data file then we send empty responses
    :param first_resps: the first responses to send
    :yield: the API response
    """
    empty = {"message": "", "response_code": 1, "data": []}
    for resp in first_resps:
        yield resp
    while True:
        yield empty

class TestVerifiedTab(VerifiedCourseList):

    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_parsing_duplicated(self, mock_api):
        mock_api.return_value = proctorU_api_result("duplicated")
        UserFactory(last_name="26", username="plop")

        start_date = datetime.datetime(day=01, month=04, year=01)
        resp = utils_proctorU_api.get_proctorU_students("Cours", "Run", start_date, student_grades={})
        self.assertEqual(1, len(resp["plop"]))

    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_parsing_empty_response(self, mock_api):
        mock_api.return_value = proctorU_api_result("empty")

        start_date = datetime.datetime(day=01, month=04, year=01)
        resp = utils_proctorU_api.get_proctorU_students("Cours", "Run", start_date, student_grades={})
        self.assertEqual("Empty response from the API", resp["error"])

    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_user_aggregation(self, mock_api):
        mock_api.side_effect = simulate_procotru_multiple_resp([proctorU_api_result("student-aggregation")])
        UserFactory(last_name="26", username="plop")

        today = datetime.datetime.today()
        begin = today - datetime.timedelta(100)
        resp = utils_proctorU_api.get_proctorU_students("Cours", "Run", begin, student_grades={})
        self.assertEqual(2, len(resp["plop"]))
        self.assertEqual("Reservation created", resp["plop"][0]["ProctorNotes"])
        self.assertEqual("Reservation cancelled", resp["plop"][1]["ProctorNotes"])

    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_no_users_in_course(self, mock_api):
        mock_api.return_value = proctorU_api_result("student-aggregation")
        UserFactory(last_name="26")

        start_date = datetime.datetime(day=01, month=04, year=01)
        resp = utils_proctorU_api.get_proctorU_students("No one", "likes me", start_date, student_grades={})
        self.assertIn("id", resp["warn"])
        self.assertIn("start", resp["warn"])
        self.assertIn("end", resp["warn"])

    def test_proctorU_query_api(self):
        ResponseRequest = namedtuple("ResponseRequest", "content")
        val = json.dumps({"test": "val", "response_code": 1})
        respMock = ResponseRequest(content=val)
        request_mock = Mock(return_value=respMock)
        data = {}
        resp = utils_proctorU_api.query_api(request_mock, "example.com", data)
        self.assertEqual(json.loads(val), resp)
        self.assertIn("time_sent", data)

    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_multiple_query_api(self, mock_api):
        mock_api.side_effect = simulate_procotru_multiple_resp(proctorU_api_result("multiple_queries"))
        UserFactory(last_name="26", username="plop")

        today = datetime.datetime.today()
        begin = today - datetime.timedelta(100)
        resp = utils_proctorU_api.get_proctorU_students("Cours", "Run", begin, student_grades={})
        self.assertEqual(4, len(resp["plop"]))
        self.assertEqual("Reservation created1", resp["plop"][0]["ProctorNotes"])
        self.assertEqual("Reservation cancelled1", resp["plop"][1]["ProctorNotes"])
        self.assertEqual("Reservation created2", resp["plop"][2]["ProctorNotes"])
        self.assertEqual("Reservation cancelled2", resp["plop"][3]["ProctorNotes"])


class TestProctoruUtils(BaseTestCase):
    def test_split_date_range(self):
        start_date = datetime.datetime(day=01, month=04, year=01)
        end_date = start_date + datetime.timedelta(34)

        dr = list(utils_proctorU_api.split_large_date_range(start_date, end_date, 1))
        self.assertEqual(34, len(dr))
        self.assertTrue(all([len(d) == 2 for d in dr]))
        self.assertEqual(start_date, dr[0][0])

        dr = list(utils_proctorU_api.split_large_date_range(start_date, end_date, 34))
        self.assertEqual(1, len(dr))
        self.assertTrue(all([len(d) == 2 for d in dr]))

        dr = list(utils_proctorU_api.split_large_date_range(start_date, end_date, 200))
        self.assertEqual(1, len(dr))
        self.assertEqual(end_date, dr[-1][1])
