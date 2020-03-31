# -*- coding: utf-8 -*-

from django.core import mail
from django.core.management import call_command
from django.test.utils import override_settings

from bs4 import BeautifulSoup

from opaque_keys.edx.keys import CourseKey
from student.tests.factories import UserFactory, CourseEnrollmentFactory
from student.models import CourseEnrollment
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from courses.tests.factories import CourseFactory
from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class AuditToHonorTestCase(ModuleStoreTestCase):
    """ Tests that the command correctly changes
        `audit` course modes to `honor`"""

    def setUp(self):
        super(AuditToHonorTestCase, self).setUp()
        self.course1 = CourseFactory(key='fun/1/1')
        self.course2 = CourseFactory(key='fun/2/2')
        # Create 3 `audit` CourseEnrollment
        CourseEnrollmentFactory(course_id=self.course1.key, mode='honor')
        CourseEnrollmentFactory(course_id=self.course1.key, mode='audit')
        CourseEnrollmentFactory(course_id=self.course1.key, mode='verified')
        CourseEnrollmentFactory(course_id=self.course2.key, mode='audit')
        CourseEnrollmentFactory(course_id=self.course2.key, mode='audit')

    def test_audit_to_honor(self):
        """
        Ensure, all `audit` enrollments have been changed to `honor` as
        `verified` ones should be left unchanged
        """
        call_command('course_mode_audit_to_honor')
        self.assertEqual(5, CourseEnrollment.objects.all().count())
        ck1 = CourseKey.from_string(self.course1.key)
        ck2 = CourseKey.from_string(self.course2.key)
        self.assertEqual(2, CourseEnrollment.objects.filter(course_id=ck1, mode='honor').count())
        self.assertEqual(2, CourseEnrollment.objects.filter(course_id=ck2, mode='honor').count())
        self.assertEqual(1, CourseEnrollment.objects.filter(course_id=ck1, mode='verified').count())
        self.assertEqual(0, CourseEnrollment.objects.filter(course_id=ck1, mode='audit').count())
        self.assertEqual(0, CourseEnrollment.objects.filter(course_id=ck2, mode='audit').count())

    @override_settings(PLATFORM_NAME='TEST')
    def test_report_email(self):
        """
        Email report should be sent
        """
        call_command('course_mode_audit_to_honor')
        self.assertEqual(len(mail.outbox), 1)
        # Email subject should be prefixed by [PLATFORM_NAME]
        self.assertTrue(mail.outbox[0].subject.startswith('[TEST]'))
        # Email should contain right count of updated objects
        self.assertIn("3 CourseEnrollment objects updated.", mail.outbox[0].body)
