from django.test import RequestFactory

from certificates.models import GeneratedCertificate, CertificateStatuses
from opaque_keys.edx.locator import CourseKey
from student.models import User
from xmodule.modulestore.django import modulestore
from courseware import grades as courseware_grades


store = modulestore()


ASSIGNMENT_SHORT_NAME = 'Certif Avg'


class StudentCertificateHandler(object):

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
            if section['label'] == ASSIGNMENT_SHORT_NAME:
                self.grade = section['percent']
        return self.grade

    def is_eligible_for_certificate(self):
        return self.get_certificate_grade() >= self.passing_grade

    def add_certificate_generation_entry(self):
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
