# -*- coding: utf-8 -*-

from collections import namedtuple
import json
import os

from mock import patch, Mock

from student.tests.factories import CourseEnrollmentFactory, UserFactory

from django.core.urlresolvers import reverse
from test_course_list import VerifiedCourseList

from .. import utils_proctorU_api
from bs4 import BeautifulSoup

def proctorU_api_result(test_key):
    path = os.path.dirname(__file__)
    json_path = os.path.join(path, "proctoru_data.json")
    obj = json.loads(open(json_path).read())
    return obj[test_key]


class TestVerifiedTab(VerifiedCourseList):
    def setUp(self):
        super(TestVerifiedTab, self).setUp()
        self.get_proctorU_students = utils_proctorU_api.get_proctorU_students
    
    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_parsing_duplicated(self, mock_api):
        mock_api.return_value = proctorU_api_result("duplicated")
        user = UserFactory(last_name="26", username="plop")

        resp = utils_proctorU_api.get_proctorU_students(course_name="Cours",
                                                        course_run="Run",
                                                        student_grades={})
        self.assertEqual(1, len(resp["plop"]))


    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_parsing_empty_response(self, mock_api):
        mock_api.return_value = proctorU_api_result("empty")

        resp = utils_proctorU_api.get_proctorU_students(course_name="Cours",
                                                        course_run="Run",
                                                        student_grades={})
        self.assertEqual("Empty response from the API", resp["error"])


    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_user_aggregation(self, mock_api):
        mock_api.return_value = proctorU_api_result("student-aggregation")
        user = UserFactory(last_name="26", username="plop")

        resp = utils_proctorU_api.get_proctorU_students(course_name="Cours",
                                                        course_run="Run",
                                                        student_grades={})
        self.assertEqual(2, len(resp["plop"]))
        self.assertEqual("Reservation created", resp["plop"][0]["ProctorNotes"])
        self.assertEqual("Reservation cancelled", resp["plop"][1]["ProctorNotes"])


    @patch("backoffice.utils_proctorU_api.query_api")
    def test_proctorU_api_no_users_in_course(self, mock_api):
        mock_api.return_value = proctorU_api_result("student-aggregation")
        user = UserFactory(last_name="26")

        resp = utils_proctorU_api.get_proctorU_students(course_name="No one",
                                                        course_run="likes me",
                                                        student_grades={})
        self.assertIn("id", resp["warn"])
        self.assertIn("start", resp["warn"])
        self.assertIn("end", resp["warn"])


    # @patch("backoffice.utils_proctorU_api.query_api")
    # @patch("backoffice.utils_proctorU_api.get_proctorU_header")
    # @patch("backoffice.utils_proctorU_api.get_proctorU_students")
    # def test_proctorU_api_view(self, mock_PU_stud, mock_header, mock_api):
    #     utils_proctorU_api.procterU_installed = True
    #     user = UserFactory(last_name="26")
    #
    #     mock_header.return_value = ""
    #     mock_api.return_value = proctorU_api_result("student-aggregation")
    #     mock_PU_stud.return_value = self.get_proctorU_students(course_name="Cours",
    #                                                            course_run="Run")
    #
    #     response = self.client.get(reverse('backoffice:course-verified', args=[unicode(self.course3.id)]))
    #     soup = BeautifulSoup(response.content)
    #
    #     proctor_notes = soup.find("td", {"class": "proctor-notes"})
    #     list_proctor_notes = proctor_notes.findChildren()
    #
    #     self.assertIn(user.last_name, soup.find('td', {"class":"user"}).text)
    #     self.assertIn("26", soup.find('td', {"class":"proctorU-id"}).text)
    #     self.assertIn("cancelled", list_proctor_notes[0].text)
    #     self.assertIn("list-group-item-warning", list_proctor_notes[0].html)
    #
    #     self.assertIn("created", list_proctor_notes[1].text)
    #     self.assertIn("list-group-item-succes", list_proctor_notes[1].html)
    #
    #
    #     self.assertIn(user.last_name, soup.find('td', {"class":"user"}).text)
    #     self.assertIn(user.last_name, soup.find('td', {"class":"user"}).text)


    def test_proctorU_query_api(self):
        ResponseRequest = namedtuple("ResponseRequest", "content")
        val = json.dumps({"test": "val", "response_code": 1})
        respMock = ResponseRequest(content=val)
        request_mock = Mock(return_value=respMock)
        header = {}
        data = {}
        resp = utils_proctorU_api.query_api(request_mock, "example.com", data)
        self.assertEqual(json.loads(val), resp)
        self.assertIn("time_sent", data)
