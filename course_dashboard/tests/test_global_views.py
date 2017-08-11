from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from student.models import UserProfile
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms
from .base import BaseCourseDashboardTestCase


@skipUnlessLms
class GlobalViewsTestCase(ModuleStoreTestCase):

    def setUp(self):
        password = super(GlobalViewsTestCase, self).setUp()
        UserProfile.objects.create(user=self.user)

        self.client.logout()
        self.client.login(username=self.user.username, password=password)

    def test_home(self):
        url = reverse('course-dashboard-global:home')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)

    def test_logged_out_user_is_not_allowed(self):
        self.client.logout()
        url = reverse('course-dashboard-global:home')
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_student_map(self):
        url = reverse('course-dashboard-global:student-map')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)


class GlobalStudentMapTestCase(BaseCourseDashboardTestCase):
    """
    Tests the Global Student Map view.
    """

    def setUp(self):
        super(GlobalStudentMapTestCase, self).setUp()
        self.staff = UserFactory.create(is_staff=True)
        self.client.login(username=self.staff.username, password="test")

    def get_response(self, url_name, course=None, response_format=None):
        url = reverse(url_name)
        if response_format is not None:
            url += "?format=" + response_format
        return self.client.get(url)

    def get_global_student_map(self, response_format=None):
        return self.get_response("course-dashboard-global:student-map", response_format=response_format)

    def test_student_map(self):
        response = self.get_global_student_map()

        self.assertEqual(200, response.status_code)

    def test_non_empty_student_map(self):
        self.enroll_student(self.course, user__profile__country='FR')
        response = self.get_global_student_map()
        self.assertEqual(200, response.status_code)
        self.assertIn("France", response.content)

    def test_student_has_no_access(self):
        student = UserFactory.create()
        self.client.login(username=student.username, password="test")
        response = self.get_global_student_map()
        self.assertEqual(404, response.status_code)

    def test_instructor_has_no_access(self):
        self.client.login(username=self.instructor.username, password="test")
        response = self.get_global_student_map()
        self.assertEqual(404, response.status_code)

    def test_csv_response(self):
        self.enroll_student(self.course, user__profile__country='FR')

        response = self.get_global_student_map(response_format="csv")
        rows = self.get_csv_response_rows(response)

        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(rows))
        self.assertEqual([_("France"), "1"], rows[1])
