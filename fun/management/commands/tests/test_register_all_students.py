from django.core.management import call_command

from student.tests.factories import UserFactory
from student.models import CourseEnrollment

from course_dashboard.tests.base import BaseCourseDashboardTestCase


class RegisterAllStudentsTestCase(BaseCourseDashboardTestCase):
    """Tests for command register_all_students.py"""

    def is_enrolled(self, course_key, user):
        return CourseEnrollment.objects.filter(user=user,
                                               course_id=course_key).exists()

    def test_register_all_students(self):
        users = UserFactory.create_batch(size=10)
        for user in users:
            self.assertFalse(self.is_enrolled(self.course.id, user))

        call_command('register_all_students',
                     course=self.get_course_id(self.course))

        for user in users:
            self.assertTrue(self.is_enrolled(self.course.id, user))

    def test_unactive_student_stay_inactive(self):
        user = UserFactory.create()
        enrollment = self.enroll_student(self.course, user=user)
        self.assertTrue(self.is_enrolled(self.course.id, user))
        enrollment.is_active = False
        call_command('register_all_students',
                     course=self.get_course_id(self.course))
        self.assertFalse(enrollment.is_active)

