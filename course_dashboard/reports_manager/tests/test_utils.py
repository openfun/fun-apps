# -*- coding: utf-8 -*-

from xmodule.modulestore.tests.factories import ItemFactory

from course_dashboard.reports_manager import utils
from course_dashboard.tests.base import BaseCourseDashboardTestCase

class UtilsTestCase(BaseCourseDashboardTestCase):
    def test_build_answers_distribution_report_name(self):
        problem_name = u"Quizz trés fà  cile."
        problem = ItemFactory(parent=self.course,
                              category='problem',
                              display_name=problem_name)
        report_name = utils.build_answers_distribution_report_name(problem)
        assert report_name
