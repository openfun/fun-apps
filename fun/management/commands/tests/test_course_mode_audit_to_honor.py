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
    """ Tests that the command correctly change
        audit coursemodes to honor"""

    def setUp(self):
        super(AuditToHonorTestCase, self).setUp()
        self.course1 = CourseFactory(key='fun/1/1')
        self.course2 = CourseFactory(key='fun/2/2')
        CourseEnrollmentFactory(course_id=self.course1.key, mode='honor')
        CourseEnrollmentFactory(course_id=self.course1.key, mode='audit')
        CourseEnrollmentFactory(course_id=self.course1.key, mode='verified')
        CourseEnrollmentFactory(course_id=self.course2.key, mode='audit')
        CourseEnrollmentFactory(course_id=self.course2.key, mode='audit')

    def test_audit_to_honor(self):
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
        call_command('course_mode_audit_to_honor')
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.startswith('[TEST]'))
        soup = BeautifulSoup(mail.outbox[0].alternatives[0][0])  # html content
        trs = soup.findAll('tr', class_='course')
        self.assertEqual(self.course1.key, str(trs[0].findAll('td')[0].text.strip()))
        self.assertEqual(u"1", trs[0].findAll('td')[1].text.strip())
        self.assertEqual(self.course2.key, str(trs[1].findAll('td')[0].text.strip()))
        self.assertEqual(u"2", trs[1].findAll('td')[1].text.strip())
