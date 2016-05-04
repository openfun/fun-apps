from django.test import RequestFactory

from certificates.models import GeneratedCertificate, CertificateStatuses
from opaque_keys.edx.locator import CourseKey
from student.models import User
from xmodule.modulestore.django import modulestore
from courseware import grades as courseware_grades
from student.models import CourseEnrollment


store = modulestore()


ASSIGNMENT_VALID_SHORT_NAMES = ('certificat avg', 'certificat')


class StudentCertificateHelper(object):
    '''
    Provides helpers for managing the verified certificate for a single
    student enrolled to a given course.

    ## Usage example:

        from backoffice.certificate_manager import verified
        helper = verified.StudentCertificateHelper(
            course_key_string='Org/Course/101',
            student_username='user1',
            passing_grade=0.5
        )
        helper.get_certificate_grade()

        [out]: 0.75
    '''

    def __init__(self, course_key_string, student_username, passing_grade=0.5):
        self.course_key_string = course_key_string
        self.student_username = student_username
        self.passing_grade = passing_grade
        self.course_key = CourseKey.from_string(course_key_string)
        self.course = store.get_course(self.course_key)
        self.student = User.objects.get(username=self.student_username)
        self.grade = None

    def get_certificate_grade(self):
        request = RequestFactory().get('/')
        request.session = {}
        request.user = self.student
        grades = courseware_grades.grade(self.student, request, self.course)
        sections_grades = grades['section_breakdown']
        for section in sections_grades:
            if section['label'].lower() in ASSIGNMENT_VALID_SHORT_NAMES:
                self.grade = section['percent']
        return self.grade

    def is_eligible_for_certificate(self):
        return self.get_certificate_grade() >= self.passing_grade

    def add_certificate_generation_entry(self):
        '''
        Try adding an entry to the generated certificate table.
        Updates the entry if it exists already.
        Returns True/False to indicate whether a new an entry way added.
        Return None if the student is not eligible for verified certificate.
        '''
        if not self.is_eligible_for_certificate():
            return None
        cert, created = GeneratedCertificate.objects.get_or_create(
            user=self.student, course_id=self.course_key,
        )
        cert.status = CertificateStatuses.downloadable
        # TODO: Why do we need to cast here ?
        cert.grade = '{0:.2f}'.format(self.grade)
        cert.download_url = 'http://todo_certificate-url.com/'
        cert.save()
        return created


class CourseCertificateHelper(object):
    '''
    Provides helpers for working with verified certificates for students
    enrolled to a given course.

    ## Usage example:

        from backoffice.certificate_manager import verified
        helper = verified.CourseCertificateHelper(course_key_string='T/T/T', passing_grade=0.16)
        helper.get_student_grades()

        [out]:
        {u'user1': {'grade': 0.5, 'passed': True},
         u'user3': {'grade': 0.0, 'passed': False}}
    '''

    def __init__(self, course_key_string, passing_grade=0.5):
        self.course_key_string = course_key_string
        self.passing_grade = passing_grade
        self.course_key = CourseKey.from_string(course_key_string)

    def get_student_grades(self):
        '''
        Returns a document containing the grade for each verified
        student on the given course. Also indicate if the student's
        grade passes the certificate passing grade.
        '''
        student_grades = {}
        student_usernames = CourseEnrollment.objects.filter(
            mode='verified', course_id=self.course_key
        ).values_list('user__username', flat=True)

        for username in student_usernames:
            helper = StudentCertificateHelper(
                self.course_key_string,
                username,
                self.passing_grade,
            )
            passed = helper.is_eligible_for_certificate()
            grade = helper.grade
            student_grades[username] = {
                'passed': passed,
                'grade': grade,
            }
        return student_grades
