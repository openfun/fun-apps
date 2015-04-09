from lxml import etree
import json

from xmodule.modulestore.tests.factories import ItemFactory
from capa.correctmap import CorrectMap
from capa.tests import response_xml_factory as RF

from course_dashboard.tests.base import BaseCourseDashboardTestCase
from courseware.tests.factories import StudentModuleFactory
from course_dashboard.problem_stats.problem_monitor import ProblemMonitor
from course_dashboard.problem_stats import question_monitors as QM

class ProblemMonitorTestCase(BaseCourseDashboardTestCase):

    def _build_problem(self, *args):
        """ Build a problem string.

        Uses *args : A list of string questions (generated by ResponseXMLFactory();
                     or arbitrary xml string)
        """
        problem = etree.Element("problem")
        for string_question in args:
            xml_question = etree.fromstring(string_question)
            if xml_question.tag == 'problem':
                [problem.append(element) for element in xml_question.findall('*')]
            else:
                problem.append(xml_question)
        return etree.tostring(problem)

    def test_preprocess_problem(self):
        problem_tree = self._build_problem(RF.MultipleChoiceResponseXMLFactory().build_xml(),
                                           RF.MultipleChoiceResponseXMLFactory().build_xml(),
                                           RF.MultipleChoiceResponseXMLFactory().build_xml())
        self.problem_module.data = problem_tree
        problem_monitor = ProblemMonitor(self.problem_module)
        for question_monitor in problem_monitor.question_monitors.values():
            self.assertTrue(isinstance(question_monitor,
                                       QM.MultipleChoiceMonitor))

    def test_preprocess_problem_with_not_handled_question(self):

        problem_tree = self._build_problem(RF.MultipleChoiceResponseXMLFactory().build_xml(),
                                           RF.NumericalResponseXMLFactory().build_xml(),
                                           RF.MultipleChoiceResponseXMLFactory().build_xml())
        self.problem_module.data = problem_tree

        problem_monitor = ProblemMonitor(self.problem_module)
        question_monitors = problem_monitor.question_monitors

        self.assertEqual(len(question_monitors), 3)
        self.assertTrue(isinstance(question_monitors[self._build_question_id(0)],
                                   QM.MultipleChoiceMonitor))
        self.assertTrue(isinstance(question_monitors[self._build_question_id(1)],
                                   QM.UnhandledQuestionMonitor))
        self.assertTrue(isinstance(question_monitors[self._build_question_id(2)],
                                   QM.MultipleChoiceMonitor))
        
    def test_preprocess_problem_with_context(self):
        problem_tree = self._build_problem(RF.MultipleChoiceResponseXMLFactory().build_xml(question_text='First question, who am I ?'),
                                           "<p>Second question, whot are you ?</p>",
                                           RF.MultipleChoiceResponseXMLFactory().build_xml(question_text='Choose the best answer.'))

        self.problem_module.data = problem_tree
        problem_monitor = ProblemMonitor(self.problem_module)

        question_monitors = problem_monitor.question_monitors

        self.assertEqual(len(question_monitors), 2)
        self.assertEqual(len(question_monitors[self._build_question_id(0)].context), 1)
        self.assertEqual(len(question_monitors[self._build_question_id(1)].context), 2)
        for element in question_monitors[self._build_question_id(1)].context:
            self.assertEqual(element.tag, 'p')

    def _build_question_id(self, index):
        return "{}_{}_1".format(self.problem_module.location.html_id(),
                                index + 2)

    def _build_correct_map(self, *args):
        cmap = CorrectMap()
        for index, correctness in enumerate(args):
            cmap.update(CorrectMap(answer_id=self._build_question_id(index),
                                   correctness=correctness))
        return cmap.cmap

    def _build_student_answers(self, *args):
        student_answers = {}
        for index, response in enumerate(args):
            student_answers[self._build_question_id(index)] = response
        return student_answers

    def _build_student_module_state(self, correct_map, student_answers,
                                    seed='1', done='True', attempts=1,
                                    last_submission_time="2015-04-01T15:53:28Z"):
        state = {
            'correct_map': correct_map,
            'student_answers': student_answers,
            'input_state': None,
            'seed': seed,
            'done': done,
            'attempts' : attempts,
            'last_submission_time' : last_submission_time
        }
        return state

    def test_get_student_answers(self):
        first_question = RF.MultipleChoiceResponseXMLFactory().build_xml(
            choices=[True, False, False])

        second_question = RF.MultipleChoiceResponseXMLFactory().build_xml(
            choices=[False, True, False])

        self.problem_module.data = self._build_problem(first_question, second_question)
        problem_monitor = ProblemMonitor(self.problem_module)

        cmap = self._build_correct_map('correct', 'incorrect')
        student_answers = self._build_student_answers('choice_0', 'choice_2')

        StudentModuleFactory(course_id=self.course.id,
                             state=self._build_student_module_state(cmap, student_answers))

        problem_monitor.get_student_answers()

        correctness_first_question = problem_monitor.question_monitors[self._build_question_id(0)].correctness
        student_answers_first_question = problem_monitor.question_monitors[self._build_question_id(1)].student_answers
        correctness_second_question = problem_monitor.question_monitors[self._build_question_id(1)].correctness
        student_answers_second_question = problem_monitor.question_monitors[self._build_question_id(1)].student_answers

        self.assertDictContainsSubset(correctness_first_question, {'correct' : 1, 'incorrect' : 0})
        self.assertDictContainsSubset(student_answers_first_question, {'choice_0' : 1})
        self.assertDictContainsSubset(correctness_second_question, {'correct' : 0, 'incorrect' : 1})
        self.assertDictContainsSubset(student_answers_second_question, {'choice_2' : 1})
