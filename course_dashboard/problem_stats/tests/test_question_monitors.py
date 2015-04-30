from collections import defaultdict
from lxml import etree

from django.test import TestCase

import capa.inputtypes as inputtypes
from capa.tests import response_xml_factory as RF

from course_dashboard.tests.base import BaseCourseDashboardTestCase
from course_dashboard.problem_stats.question_monitors import QuestionMonitor, ChoiceQuestionMonitor

class QuestionMonitorTestCase(BaseCourseDashboardTestCase):

    def setUp(self):
        problem_tree = RF.MultipleChoiceResponseXMLFactory().build_xml()
        question_tree = etree.fromstring(problem_tree).find('multiplechoiceresponse')
        self.label_text = "What colour was Henri IV's white horse?"
        question_tree = self.add_label_to_choicegroup(question_tree,
                                                      self.label_text)

        self.question_monitor = QuestionMonitor(1, question_tree, None)

        self.question_monitor.student_answers = {'choice_0' : 10,
                                                 'choice_1' : 42}
        self.question_monitor.correctness = {'correct' : '10',
                                             'incorrect' : '42'}

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

    def test_title(self):
        self.assertEqual(self.label_text, self.question_monitor.get_title()[0].text)
        self.assertIn(self.label_text, self.question_monitor.get_html('problem_stats/multiplechoice.html'))

class ChoiceQuestionMonitorTestCase(TestCase):
    def setUp(self):
        problem_tree = RF.ChoiceResponseXMLFactory().build_xml(choice_type='checkbox',
                                                               choices=[True, True, False],
                                                               choice_names=['henri2','henri1','charles8'])
        question_tree = etree.fromstring(problem_tree).find('choiceresponse')
        self.question_monitor = ChoiceQuestionMonitor(1, question_tree, None)
        self.question_monitor.student_answers = {"[u'choice_0',u'choice_2']": 10,
                                                 "[u'choice_0',u'choice_1']": 42}
    def test_parse_student_answers(self):
        self.question_monitor._parse_student_answers()
        self.assertEqual(self.question_monitor.student_answers,
                         {(1, 3) : 10, (1, 2) :42})
