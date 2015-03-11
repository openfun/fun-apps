from .base import BaseCourseDashboardTestCase

class AnswerDistributionTestCase(BaseCourseDashboardTestCase):
    def test_one_response(self):
        self.create_student_module()
        
