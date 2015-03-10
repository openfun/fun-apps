import csv
from StringIO import StringIO

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from courseware.tests.factories import InstructorFactory
from student.tests.factories import CourseEnrollmentFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.django_utils import TEST_DATA_MOCK_MODULESTORE
from xmodule.modulestore.tests.factories import CourseFactory


@override_settings(MODULESTORE=TEST_DATA_MOCK_MODULESTORE)
class BaseCourseDashboardTestCase(ModuleStoreTestCase):

    def setUp(self):
        super(BaseCourseDashboardTestCase, self).setUp(create_user=False)

        self.course = CourseFactory.create()
        instructor = InstructorFactory.create(course_key=self.course.id)
        self.client.login(username=instructor.username, password="test")

    def enroll_student(self, course, **kwargs):
        return CourseEnrollmentFactory.create(
            course_id=self.get_course_id(course),
            **kwargs
        )

    def get_course_id(self, course):
        return course.id.to_deprecated_string()

    def get_course_url(self, url_name, course, response_format=None):
        return self.get_url(url_name, self.get_course_id(course), response_format=response_format)

    def get_url(self, url_name, course_id, response_format=None):
        url = reverse(url_name, kwargs={"course_id": course_id})
        if response_format is not None:
            url += "?format=" + response_format
        return self.client.get(url)

    def get_csv_response_rows(self, response):
        response_content = StringIO(response.content)
        response_content.seek(0)
        return [row for row in csv.reader(response_content)]
