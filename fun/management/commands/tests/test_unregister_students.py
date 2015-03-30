 # -*- coding: utf-8 -*-

import os
import tempfile

from django.core.management import call_command
from django.utils.six import StringIO

from student.tests.factories import UserFactory
from student.models import CourseEnrollment

from course_dashboard.tests.base import BaseCourseDashboardTestCase
from fun.management.commands.unregister_students import Command

class RegisterAllStudentsTestCase(BaseCourseDashboardTestCase):
    """Tests for command register_all_students.py."""

    def setUp(self):
        super(RegisterAllStudentsTestCase, self).setUp()
        self.output_error = StringIO()
        self.output = StringIO()
        self.err_msg = Command.err_msg

    def enroll_students(self, course, *args):
        for user in args:
            self.enroll_student(course, user=user)

    def unregister_student(self, input_file):
        call_command('unregister_students',
                     course=self.get_course_id(self.course),
                     input_file=input_file.name,
                     stderr=self.output_error)
        input_file.close()

    def create_input_file(self, *args):
        """Create a well formated input file as required."""
        input_file = tempfile.NamedTemporaryFile()
        for email in args:
            input_file.write(u"{}\n".format(email).encode('utf-8'))
        # ensure data is written to disk.
        input_file.flush()
        os.fsync(input_file)

        return input_file

    def test_unregister_students(self):
        users = UserFactory.create_batch(size=20)
        self.enroll_students(self.course, *users)
        for user in users:
            self.assertTrue(CourseEnrollment.is_enrolled(user, self.course.id))
        input_file = self.create_input_file(*[user.email for user in users])

        self.unregister_student(input_file)

        for user in users:
            self.assertFalse(CourseEnrollment.is_enrolled(user, self.course.id))

    def test_unregister_students_with_unknown_email_address(self):
        user = UserFactory.create()
        self.enroll_student(self.course, user=user)
        fake_email = 'fake_email@openfun.fr'
        input_file = self.create_input_file(fake_email, user.email)

        self.unregister_student(input_file)

        self.assertIn(self.err_msg.format(fake_email,
                                          self.get_course_id(self.course)),
                      self.output_error.getvalue())
        self.assertFalse(CourseEnrollment.is_enrolled(user,
                                                      self.course.id))

    def test_unregister_students_with_not_register_student(self):
        user = UserFactory.create()
        input_file = self.create_input_file(user.email)

        self.unregister_student(input_file)

        self.assertIn(self.err_msg.format(user.email,
                                          self.get_course_id(self.course)),
                      self.output_error.getvalue())

    def test_unregister_students_with_empty_input_file(self):
        input_file = self.create_input_file("")

        self.unregister_student(input_file)

        self.assertIn(self.err_msg.format('',
                                          self.get_course_id(self.course)),
                      self.output_error.getvalue())

    def test_unregister_students_with_unicode_email(self):
        user = UserFactory.create(email=u"pépè@example.com")
        self.enroll_student(self.course, user=user)
        input_file = self.create_input_file(user.email)

        self.unregister_student(input_file)

        self.assertFalse(CourseEnrollment.is_enrolled(user,
                                                      self.course.id))
