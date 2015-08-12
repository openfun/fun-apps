from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from course_dashboard.problem_stats.utils import build_course_tree
from course_dashboard.problem_stats.tests import sample_courses

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class BuildCourseTreeTestCase(ModuleStoreTestCase):
    def setUp(self):
        super(BuildCourseTreeTestCase, self).setUp()
        self.course_key = self.create_sample_course('FUN', 'toy', 'SPRING_2015',
                                                    block_info_tree=sample_courses.problem_block_info_tree)
        self.course = self.store.get_course(self.course_key)

    def test_build_json_tree(self):
        tree = {'text': 'Empty',
                'a_attr': {'href': '#'},
                'state': {'opened': True},
                'children': [
                    {'text': 'N/A',
                     'a_attr': {'href': '#'},
                     'state': {'opened': True},
                     'children': [
                         {'text': 'N/A',
                          'a_attr': {'href': '#'},
                          'state': {'opened': True},
                          'children': [
                              {'text': 'N/A',
                               'a_attr': {'href': '#'},
                               'state': {'opened': True},
                               'children': [
                                   {'text': u"Blank Advanced Problem",
                                    'a_attr': {'href': "/courses/{}/fun/dashboard/problem_stats/get_stats/89b2ed2a06ce4f9f8dcd26fee087b60a".format(str(self.course.id))},
                                    'state': {'opened': True},
                                    'children': [],
                                    'li_attr': {'category': 'problem',
                                                'report_url': "/courses/{}/fun/dashboard/reports_manager/generate/89b2ed2a06ce4f9f8dcd26fee087b60a/".format(str(self.course.id))},
                                    'icon': 'glyphicon glyphicon-pencil'}],
                               'li_attr': {'category': 'other', 'report_url': '#'},
                               'icon': 'default'}],
                          'li_attr': {'category': 'other', 'report_url': '#'},
                          'icon': 'default'}],
                     'li_attr': {'category': 'other', 'report_url': '#'},
                     'icon': 'default'}],
                'li_attr': {'category': 'other', 'report_url': '#'},
                'icon': 'default'}
        course_tree = build_course_tree(self.course)
        self.maxDiff=None
        self.assertEqual(tree, course_tree)
