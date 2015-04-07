from course_dashboard.tests.base import BaseCourseDashboardTestCase
from django.core.urlresolvers import reverse
import random
import hashlib

class ProblemStatsViewTestCase(BaseCourseDashboardTestCase):
    def test_index(self):
        self._generate_modules_tree(self.course,
                                    'chapter', 'sequential',
                                    'vertical', 'problem')
        response = self.get_response("course-dashboard:problem-stats:index",
                                     self.course)
        self.assertEqual(200, response.status_code)

    def test_get_stats(self):
        url = reverse("course-dashboard:problem-stats:get-stats",
                      kwargs={"course_id": self.get_course_id(self.course)})
        response = self.client.get(url, {'problem_id' : self.problem_module.location.name})
        self.assertEqual(200, response.status_code)
