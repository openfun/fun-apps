from capa.tests import response_xml_factory as RF
from xmodule.modulestore.tests.factories import ItemFactory
from xmodule.capa_module import CapaDescriptor

from course_dashboard.tests.base import BaseCourseDashboardTestCase
from course_dashboard.problem_stats import utils


class UtilsTestCase(BaseCourseDashboardTestCase):
    def test_fetch_problems(self):
        ItemFactory(parent=self.course, category='problem', display_name='problem1')
        ItemFactory(parent=self.course, category='problem', display_name='problem2')
        problems = utils.fetch_problems(self.store, self.course.id)
        self.assertEqual(len(problems), 3)
        for problem in problems:
            self.assertTrue(isinstance(problem, CapaDescriptor))

    def test_fetch_problem_with_id(self):
        problem_id = 'problem1'
        ItemFactory(parent=self.course, category='problem', display_name=problem_id)
        problem = utils.fetch_problem(self.store, self.course.id, problem_id=problem_id)
        self.assertTrue(problem, isinstance(problem, CapaDescriptor))

    def test_fetch_ancestors_names(self):
        self._generate_modules_tree_with_display_names(self.course,
                                                       'chapter', 'sequential',
                                                       'vertical', 'problem')

        ancestors = utils.fetch_ancestors_names(self.store, self.problem_module.location)
        self.assertEqual(ancestors, [self.course.display_name, 'chapter',
                                     'sequential', 'vertical'])

    def test_get_problem_size(self):
        self.problem_module.data = RF.MultipleChoiceResponseXMLFactory().build_xml()
        size = utils.get_problem_size(self.problem_module)
        self.assertEqual(size, 1)
