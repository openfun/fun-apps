import os
from mock import patch

from django.conf import settings

from certificates.models import GeneratedCertificate
from student.tests.factories import CourseEnrollmentFactory, UserProfileFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from backoffice.certificate_manager import tasks
from courses.tests.factories import CourseFactory as FunCourseFactory
from courses.tests.factories import CourseUniversityRelationFactory
from universities.tests.factories import UniversityFactory
from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class CertificateTests(ModuleStoreTestCase):

    def setUp(self):
        super(CertificateTests, self).setUp()
        self.course = CourseFactory.create()
        UserProfileFactory.create(user=self.user)

    def configure_course(self):
        """
        Make sure that all the right course models exist for generating the certificate.
        """
        fun_course = FunCourseFactory(key=unicode(self.course.id))
        fun_university = UniversityFactory.create()
        CourseUniversityRelationFactory(course=fun_course, university=fun_university)

    def test_get_enrolled_students(self):
        user_count_before_enrollment = tasks.get_enrolled_students_count(self.course.id)
        CourseEnrollmentFactory(course_id=self.course.id, user=self.user)
        user_count_after_enrollment = tasks.get_enrolled_students_count(self.course.id)

        self.assertEqual(0, user_count_before_enrollment)
        self.assertEqual(1, user_count_after_enrollment)

    @patch("backoffice.certificate_manager.utils.make_certificate_hash_key")
    def test_generate_test_certificate(self, mock_make_certificate_hash_key):
        self.configure_course()
        mock_make_certificate_hash_key.return_value = "dummyhash"
        test_certificate_path = os.path.join(
            settings.CERTIFICATES_DIRECTORY,
            "TEST_attestation_suivi_{}_dummyhash.pdf".format(unicode(self.course.id).replace("/", "_"))
        )
        if os.path.exists(test_certificate_path):
            os.remove(test_certificate_path)

        tasks.create_test_certificate(self.course.id)
        self.assertTrue(os.path.exists(test_certificate_path))

    def test_generate_course_certificates(self):
        self.configure_course()
        CourseEnrollmentFactory(course_id=self.course.id, user=self.user)

        certificate_count_before = GeneratedCertificate.objects.count()
        with patch('instructor_task.tasks_helper._get_current_task'):
            tasks.generate_course_certificates(self.course.id, "certified")
        certificate_count_after = GeneratedCertificate.objects.count()

        self.assertEqual(0, certificate_count_before)
        self.assertEqual(1, certificate_count_after)
