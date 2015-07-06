import json

from django.core.urlresolvers import reverse

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from fun.tests.utils import skipUnlessCms


@skipUnlessCms
class TestVideoUpload(ModuleStoreTestCase):

    def setUp(self):
        super(TestVideoUpload, self).setUp(create_user=False)
        self.course = CourseFactory.create()
        instructor = InstructorFactory.create(course_key=self.course.id)
        self.client.login(username=instructor.username, password="test")

    def test_api_videos_with_no_university(self):
        url = reverse("videoupload:videos", kwargs={"course_key_string": self.course.id})
        response = self.client.get(url)
        data = json.loads(response.content)

        self.assertIn("error", data)
