import ast

from collections import defaultdict
from lxml import etree

from django.template.loader import render_to_string

from capa.registry import TagRegistry
import capa.responsetypes as loncapa_question_types


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
        label = None
        choicegroup = self.question_tree.find('choicegroup')
        if choicegroup:
            label = choicegroup.get('label')
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

    def get_html(self):
        raise NotImplementedError()

    def get_template_html(self, template_name, extra_context=None):
        """ Render the corresponding question template with it's context.

        Args:
         template_name (str): The template file corresponding to the question.

        Returns:
         str: The html as string.
        """

        total_answers = self._compute_stats()
        if not total_answers:
            return  render_to_string('problem_stats/no_answers.html', {'title' : self.get_title()})

        context = {'question_id' : self.id,
                   'question_tree' : self.question_tree,
                   'title' : self.get_title(),
                   'total_answers': total_answers,
                   'student_answers' : self.student_answers,
                   'blank_answers': self.no_answer,
                   'correctness' : self.correctness}
        if extra_context:
            context.update(extra_context)

        html = render_to_string(template_name, context)

        return html

@registry.register
class MultipleChoiceMonitor(QuestionMonitor):
    """Monitor for Multiplechoice questions"""
    tags = ['multiplechoiceresponse']

    def convert_student_answers(self):
        """Convert choice number to it's text choice.
        For Multiplechoice questions only the choice number is included in the student answer.
        Therefore we replace the choice number by it's real value as text.

        Example:
            For a question like `Which countrie is in Europe ?`
            >> self.student_answers
               {"choice_1" : 4, "choice_2" : 1}
            >> convert_student_answers()
            >> {"France" : 4, "Brazil" : 1}
        """
        student_answers = {}
        for index, choice in enumerate(self.question_tree.iter('choice')):
            student_answers[choice.text] = self.student_answers["choice_{}".format(index)]
        self.student_answers = student_answers

    def get_html(self):
        self.convert_student_answers()
        right_answer = self.question_tree.find(".//choice[@correct='true']").text
        return self.get_template_html('problem_stats/single_choice_question.html',
                                      {'right_answer' : right_answer})

@registry.register
class StringQuestionMonitor(QuestionMonitor):
    """Monitor for Multiplechoice questions"""
    tags = ['stringresponse']

    def get_html(self):
        right_answer = self.question_tree.get('answer')
        return self.get_template_html('problem_stats/single_choice_question.html',
                                      {'right_answer' : right_answer})

@registry.register
class OptionQuestionMonitor(QuestionMonitor):
    """Monitor for Multiplechoice questions"""
    tags = ['optionresponse']

    def get_html(self):
        right_answer = self.question_tree.find('optioninput').get('correct')
        return self.get_template_html('problem_stats/single_choice_question.html',
                                      {'right_answer' : right_answer})

@registry.register
class ChoiceQuestionMonitor(QuestionMonitor):
    """Monitor for Multiplechoice questions"""
    tags = ['choiceresponse']

    def _parse_student_answers(self):
        """Parses student answers from string.

        Answers for ChoiceQuestion come as a strings like u"[u'choice_0',u'choice_2']"
        To facilitate the rendering of the answer we convert the string into a tuple.
        e.g.: u"[u'choice_0',u'choice_2']" -> (1, 3)
              u"[u'choice_1',u'choice_2']" -> (2, 3)
        The first choice beeing 1 and not 0.
        """
        student_answers = {}
        for answer, value in self.student_answers.iteritems():
            choices = ast.literal_eval(answer)
            choices = [int(choice[-1:]) + 1 for choice in choices]
            student_answers[tuple(choices)] = value
        self.student_answers = student_answers

    def get_html(self):
        self._parse_student_answers()
        return self.get_template_html('problem_stats/choice_question.html')


@registry.register
class UnhandledQuestionMonitor(QuestionMonitor):
    """Monitor for unhandled questions."""

    loncapa_question_tags = loncapa_question_types.registry.registered_tags()
    monitor_question_tags = registry.registered_tags()
    tags = [tags for tags in loncapa_question_tags if tags not in monitor_question_tags]

    def get_html(self):
        return self.get_template_html('problem_stats/nothandled.html')

