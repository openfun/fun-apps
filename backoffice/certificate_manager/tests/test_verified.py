import os
from mock import patch

from django.conf import settings

from certificates.models import GeneratedCertificate
from student.tests.factories import CourseEnrollmentFactory, UserProfileFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from backoffice.certificate_manager import tasks
from backoffice.certificate_manager import verified as verified_certificate
from courses.tests.factories import CourseFactory as FunCourseFactory
from courses.tests.factories import CourseUniversityRelationFactory
from universities.tests.factories import UniversityFactory
from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class VerifiedCertificateTests(ModuleStoreTestCase):

    def setUp(self):
        super(VerifiedCertificateTests, self).setUp()
        self.course = CourseFactory.create()
        UserProfileFactory.create(user=self.user)
        self.configure_course()

    def configure_course(self):
        """
        Make sure that all the right course models exist for generating the certificate.
        """
        fun_course = FunCourseFactory(key=unicode(self.course.id))
        fun_university = UniversityFactory.create()
        CourseUniversityRelationFactory(course=fun_course, university=fun_university)

    def test_generate_test_certificate(self):
        helper = verified_certificate.StudentCertificateHelper(
            'org.0/course_0/Run_0',
            self.user.username,
            0.5
        )
