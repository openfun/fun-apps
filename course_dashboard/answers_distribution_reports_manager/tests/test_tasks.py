import textwrap

from xmodule.tests.test_capa_module import CapaFactory
from xmodule.modulestore.tests.factories import ItemFactory
from course_dashboard.tests.base import BaseCourseDashboardTestCase
from course_dashboard.answers_distribution_reports_manager import tasks
from course_dashboard.answers_distribution import get_problem_module

class TestGradesReportManagerTasks(BaseCourseDashboardTestCase):

    def test_get_problem_module_size(self):
        
        xml = textwrap.dedent("""
        <problem>
        <multiplechoiceresponse>
          <choicegroup type="MultipleChoice">
            <choice correct="false">Apple</choice>
            <choice correct="false">Banana</choice>
            <choice correct="false">Chocolate</choice>
            <choice correct ="true">Donut</choice>
          </choicegroup>
        </multiplechoiceresponse>
        <p>HELLO </p>
        <multiplechoiceresponse>
          <choicegroup type="MultipleChoice">
            <choice correct="false">Apple</choice>
            <choice correct="false">Banana</choice>
            <choice correct="false">Chocolate</choice>
            <choice correct ="true">Donut</choice>
          </choicegroup>
        </multiplechoiceresponse>
        </problem>
        """)
        
        problem_module = CapaFactory.create(xml=xml)
        self.assertEqual(2, tasks.get_problem_module_size(problem_module))        

            
    def test_create_header_row(self):
        self.assertEqual(['id', 'gender', 'year_of_birth', 'level_of_education','q1', 'q2', 'q3'],
                          tasks.create_header_row(3))

    def test_create_list_of_question_id(self):
        problem_module_id = "22220f82d19a42239ae45d73002633c6"
        course_number = '1035'
        organisation = 'cnam'
        quizz_size = 2
        list_of_question_ids = ["i4x-cnam-1035-problem-22220f82d19a42239ae45d73002633c6_2_1",
                               "i4x-cnam-1035-problem-22220f82d19a42239ae45d73002633c6_3_1"]
        
        self.assertEqual(tasks.create_list_of_question_ids(organisation,
                                                           course_number,
                                                           problem_module_id,
                                                           quizz_size),
                         list_of_question_ids)

     
     
