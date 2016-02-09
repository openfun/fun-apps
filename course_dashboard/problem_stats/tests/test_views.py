from course_dashboard.tests.base import BaseCourseDashboardTestCase
from django.core.urlresolvers import reverse

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
                      kwargs={"course_id": self.get_course_id(self.course),
                              "problem_id": self.problem_module.location.name})
        response = self.client.get(url, {'problem_id' : self.problem_module.location.name})
        self.assertEqual(200, response.status_code)

    def test_invalid_course_key_raises_404(self):
        # The staff instructor bypasses the valid course id checks
        self.instructor.is_staff = True
        self.instructor.save()
        invalid_course_id = 'not/a/validcourseid'

        response_index = self.client.get(
            reverse("course-dashboard:problem-stats:index",
                    kwargs={'course_id': invalid_course_id})
        )
        response_stats = self.client.get(
            reverse("course-dashboard:problem-stats:get-stats",
                    kwargs={"course_id": invalid_course_id,
                            "problem_id": self.problem_module.location.name}),
            {'problem_id' : self.problem_module.location.name})

        self.assertEqual(404, response_index.status_code)
        self.assertEqual(404, response_stats.status_code)
