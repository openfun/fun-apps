from collections import defaultdict
from lxml import etree

from django.template.loader import render_to_string

from capa.registry import TagRegistry
import capa.responsetypes as loncapa_question_types

from course_dashboard.problem_stats.utils import percentage

registry = TagRegistry()

class QuestionMonitor(object):
    """Class for question monitoring.

    Attributes:
        id (str): The question id. (e.g. :i4x-onequizz-onequizz-problem-28a9c8d0f76d47a2a58f8d0246ef7c67_2_1)
        context (etree.ElementTree): The question context. (surrounding xml tags)
        student_answers (defaultdict(int)): A dict mapping each answer with it's count.
            e.g. {'choice_1' : 42, 'choice_2' : 89}
                 Answer 'choice1' was found 42 times, answer 'choice2' 89 times.
        correctness (defaultdict(int)): A dict mapping the correctness with it's count.
            e.g. {'correct' : 10, 'incorrect' : 5}
                 There are 10 correct answers to the question, 5 incorrect.
        no_answer (int) : the count of blank answers.
        template_file (str) : The template file corresponding to the questions.
     """

    def  __init__(self, id, question_tree, context):
        self.id = id
        self.question_tree = question_tree
        self.context = context

        self.student_answers = defaultdict(int)
        self.no_answer = 0
        self.correctness = defaultdict(int)
        self.template_file = None

    def get_title(self):
        """
        Return the question title. If not found in 'label' attribute
        extract it from context.
        """
        label = self.question_tree.find('choicegroup').get('label')
        if label:
            title = etree.Element('p')
            title.text = label
        return [title] if label else self.context

    def _compute_stats(self):
        """Computes various student answers data.

        So far only the total number of answers is calculated.

        Returns:
            int: the sum of answers.
     """
        total_answers = sum(self.student_answers.values()) + self.no_answer
        return total_answers

    def get_html(self, template_name):
        """ Render the corresponding question template with it's context.

        Args:
         template_name (str): The template file corresponding to the question.

        Returns:
         str: The html as string.
        """

        total_answers = self._compute_stats()
        if not total_answers:
            return  u"<p>no answers</p>" # TODO a bit rough, write a better template
        context = {'question_tree' :self.question_tree,
                   'title' : self.get_title(),
                   'total_answers': total_answers,
                   'student_answers' : self.student_answers,
                   'blank_answers': self.no_answer,
                   'correctness' : self.correctness}
        html = render_to_string(template_name, context)
        return html

@registry.register
class MultipleChoiceMonitor(QuestionMonitor):
    """Monitor for Multiplechoice questions"""
    tags = ['multiplechoiceresponse']
    def get_html(self):
        return super(MultipleChoiceMonitor, self).get_html('problem_stats/multiplechoice.html')

@registry.register
class UnhandledQuestionMonitor(QuestionMonitor):
    """Monitor for unhandled questions."""

    loncapa_question_tags = loncapa_question_types.registry.registered_tags()
    monitor_question_tags = registry.registered_tags()
    tags = [tags for tags in loncapa_question_tags if tags not in monitor_question_tags]

    def get_html(self):
        return render_to_string('problem_stats/nothandled.html',
                                {'question_id' : self.id})
