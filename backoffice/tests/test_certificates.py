from mock import patch

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

    def test_get_enrolled_students(self):
        user_count_before_enrollment = tasks.get_enrolled_students_count(self.course.id)
        CourseEnrollmentFactory(course_id=self.course.id, user=self.user)
        user_count_after_enrollment = tasks.get_enrolled_students_count(self.course.id)

        self.assertEqual(0, user_count_before_enrollment)
        self.assertEqual(1, user_count_after_enrollment)

    def test_generate_course_certificates(self):
        fun_course = FunCourseFactory(key=unicode(self.course.id))
        fun_university = UniversityFactory.create()
        CourseUniversityRelationFactory(course=fun_course, university=fun_university)
        CourseEnrollmentFactory(course_id=self.course.id, user=self.user)

        certificate_count_before = GeneratedCertificate.objects.count()
        with patch('instructor_task.tasks_helper._get_current_task'):
            tasks.generate_course_certificates(self.course.id, "certified")
        certificate_count_after = GeneratedCertificate.objects.count()

        self.assertEqual(0, certificate_count_before)
        self.assertEqual(1, certificate_count_after)
