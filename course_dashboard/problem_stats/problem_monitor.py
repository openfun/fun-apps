from collections import OrderedDict
from lxml import etree
import json

import capa.responsetypes as loncapa_question_types
from courseware.models import StudentModule

from course_dashboard.problem_stats import question_monitors


class ProblemMonitor(object):
    """Main class to monitor Loncapa problems.

    Args:
         problem_module (CapaDescritptor): The problem descriptor.
             CapaDescriptor object can be retrieve from the modulestore.

    Attributes:
        problem_tree (etree.ElementTree): The xml representation of the problem.
        question_monitors (dict): A dict which map a question with it's monitor QuestionMonitor().
            e.g. :
               {"i4x-onequizz-onequizz-problem-28a9c8d0f76d47a2a58f8d0246ef7c67_2_1" : "MultipleChoiceMonitor",
                "i4x-onequizz-onequizz-problem-28a9c8d0f76d47a2a58f8d0246ef7c67_3_1" : "FormulaQuestionMonitor"}
     """

    def __init__(self, problem_module):
        self.problem_module = problem_module
        self.problem_tree = etree.XML(problem_module.data)
        self.question_monitors = OrderedDict()
        self._preprocess_problem()

    def _preprocess_problem(self):
        """Parse xml problem tree and instanciate a QuestionMonitor for each type of questions.

        Each QuestionMonitor will be store in self.question_monitors.
        """
        questions = self.problem_tree.xpath('//' + "|//".join(loncapa_question_types.registry.registered_tags()))
        for count, question in enumerate(questions):
            question_monitor_cls = question_monitors.registry.get_class_for_tag(question.tag)
            question_id = "{}_{}_1".format(self.problem_module.location.html_id(), count + 2)
            self.question_monitors[question_id] = question_monitor_cls(question_id, question,
                                                                       self._get_context(question))

    def _get_context(self, question):
        """Catch the surrounding xml context of a question.

        As problem are written by teachers. They are free to put the question title wherever they want.
        It can be found therefore inside one or two <p></p> before the question,
        or in the label attribute of the tag question itself.

        Args:
            question (etree.ElementTree):  The xml representation of the question.
        """
        context = []
        element = question.getprevious()
        while element is not None and (element.tag == 'p' or element.tag == 'legend'):
            context.append(element)
            element = element.getprevious()
        if context:
            context.reverse()
        return context

    def get_student_answers(self):
        """Gets all student problem answers(dict) from the StudentModule table.

        All answers are store in their respective question monitor (QuestionMonitor).

        Raises:
        """

        student_modules = StudentModule.objects.filter(module_state_key=self.problem_module.location)
        for student_module in student_modules:
            state = json.loads(student_module.state)
            student_answers = state.get('student_answers', None)
            correct_map = state.get('correct_map', None)
            if not student_answers or not correct_map:
                continue
            for id, question_monitor in self.question_monitors.iteritems():
                try:
                    question_monitor.correctness[correct_map[id]['correctness']] += 1
                except KeyError:
                    ## there is always a correctmap id for each question this happen when the problem have changed, TODO
                    pass
                try:
                    question_monitor.student_answers[unicode(student_answers[id])] += 1
                except KeyError:
                    question_monitor.no_answer += 1

    def get_html(self):
        """ Return problem stats as html.

        Returns:
            String : Stats on each question as html.
        """
        html = u""
        for question_monitor in self.question_monitors.values():
            html += question_monitor.get_html()
        return html
