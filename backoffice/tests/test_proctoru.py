# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import os

from mock import patch, Mock

from xmodule.modulestore.tests.factories import CourseFactory, CourseAboutFactory, ABOUT_ATTRIBUTES
from course_modes.models import CourseMode
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from universities.tests.factories import UniversityFactory

from test_course_list import VerifiedCourseList

from .. import utils_proctorU_api

def proctorU_api_result(test_key):
    path = os.path.dirname(__file__)
    json_path = os.path.join(path, "proctoru_data.json")
    obj = json.loads(open(json_path).read())
    return obj[test_key]


class TestVerifiedTab(VerifiedCourseList):
    def setUp(self):
        super(TestVerifiedTab, self).setUp()
        self.api = utils_proctorU_api.API(course_name="Cours", course_run="Run")

    @patch("backoffice.utils_proctorU_api.API.query_api")
    def test_proctorU_api_parsing_duplicated(self, mock_api):
        mock_api.return_value = proctorU_api_result("duplicated")
        UserFactory(last_name="26", username="plop")

        resp = self.api.get_proctoru_students()
        self.assertEqual(1, len(resp["plop"]))

    @patch("backoffice.utils_proctorU_api.API.query_api")
    def test_proctorU_api_parsing_empty_response(self, mock_api):
        mock_api.return_value = proctorU_api_result("empty")

        resp = self.api.get_proctoru_students()
        self.assertEqual("Empty response from the API", resp["error"])

    @patch("backoffice.utils_proctorU_api.API.query_api")
    def test_proctorU_api_user_aggregation(self, mock_api):
        mock_api.return_value = proctorU_api_result("student-aggregation")
        UserFactory(last_name="26", username="plop")

        resp = self.api.get_proctoru_students()
        self.assertEqual(2, len(resp["plop"]))
        self.assertEqual("Reservation created", resp["plop"][0]["ProctorNotes"])
        self.assertEqual("Reservation cancelled", resp["plop"][1]["ProctorNotes"])

    @patch("backoffice.utils_proctorU_api.API.query_api")
    def test_proctorU_api_no_users_in_course(self, mock_api):
        mock_api.return_value = proctorU_api_result("student-aggregation")
        UserFactory(last_name="26")

        api = utils_proctorU_api.API(course_name="No one", course_run="likes me")
        resp = api.get_proctoru_students()
        self.assertIn("id", resp["warn"])
        self.assertIn("start", resp["warn"])
        self.assertIn("end", resp["warn"])

    def test_proctorU_query_api(self):
        ResponseRequest = namedtuple("ResponseRequest", ["content", "status_code"])
        val = json.dumps({"test": "val", "response_code": 1})
        respMock = ResponseRequest(content=val, status_code=200)
        request_mock = Mock(return_value=respMock)
        api = utils_proctorU_api.API(course_name="Cours", course_run="Run", base_url="http://example.com/")
        resp = api.query_api(request_mock, "http://example.com/api")
        self.assertEqual(json.loads(val), resp)
        self.assertIn("time_sent", api.request_data)

    def test_proctorU_resp500(self):
        ResponseRequest = namedtuple("ResponseRequest", ["content", "status_code"])
        val = json.dumps({"test": "val", "response_code": 1})
        respMock = ResponseRequest(content=val, status_code=500)
        request_mock = Mock(return_value=respMock)
        api = utils_proctorU_api.API(course_name="Cours", course_run="Run", base_url="http://example.com/")
        resp = api.query_api(request_mock, "http://example.com/api")
        self.assertIn("error", resp)


class TestCommandUsersWithoutReservation(VerifiedCourseList):

    def setUp(self):
        super(TestCommandUsersWithoutReservation, self).setUp()
        self.user_not_registered_proctor = UserFactory(username="Not_registered")
        CourseEnrollmentFactory(course_id=self.course4.id, user=self.user_not_registered_proctor, mode='verified')


    @patch("backoffice.utils_proctorU_api.API.get_proctoru_students")
    def test_empty_reservation_list(self, mock_api):
        mock_api.return_value = proctorU_api_result("reservation_list_empty")

        not_registered_students = list(utils_proctorU_api.get_verified_students_without_proctoru_reservations(unicode(self.course4.id)))
        self.assertEqual(1, len(not_registered_students))
        self.assertEqual(self.user_not_registered_proctor, not_registered_students[0])


    @patch("backoffice.utils_proctorU_api.API.get_proctoru_students")
    def test_reservation_list(self, mock_api):
        user_registered_proctor = UserFactory(username="Registered")
        CourseEnrollmentFactory(course_id=self.course4.id, user=user_registered_proctor, mode='verified')
        mock_api.return_value = [[{"user": user_registered_proctor}]]

        not_registered_students = list(utils_proctorU_api.get_verified_students_without_proctoru_reservations(unicode(self.course4.id)))
        self.assertEqual(1, len(not_registered_students))
        self.assertEqual(self.user_not_registered_proctor, not_registered_students[0])
