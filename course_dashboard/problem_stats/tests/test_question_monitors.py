from collections import defaultdict
from lxml import etree

import capa.inputtypes as inputtypes
from capa.tests import response_xml_factory as RF

from course_dashboard.tests.base import BaseCourseDashboardTestCase
from course_dashboard.problem_stats.question_monitors import QuestionMonitor, MultipleChoiceMonitor

class QuestionMonitorTestCase(BaseCourseDashboardTestCase):
    def add_label_to_choicegroup(self, question_tree, label_text):
        """
        response_xml_factory doesn't provide a way to specify a label
        for a choicegroup.
        This method add 'label' attribute to the question choicegroup.
        """

        input_tags = inputtypes.registry.registered_tags()
        for choicegroup in  question_tree.xpath('//' + "|//".join(input_tags)):
            choicegroup.set('label', label_text)
        return question_tree

    def test_get_title(self):
        problem_tree = RF.MultipleChoiceResponseXMLFactory().build_xml()
        problem_tree = etree.fromstring(problem_tree)
        question_tree = problem_tree.find('multiplechoiceresponse')


        label_text = "What colour was Henri IV's white horse?"
        question_tree = self.add_label_to_choicegroup(question_tree, label_text)

        qm = QuestionMonitor(1, question_tree, None)
        self.assertEqual("What colour was Henri IV's white horse?", qm.get_title())

