from django.test import RequestFactory

from courseware import grades as courseware_grades
from student.models import User
from xmodule.modulestore.django import modulestore

from courses.models import Course

ASSIGNMENT_VALID_SHORT_NAMES = ('certificat avg', 'certificat')


def get_student_certificate_grade(course_id, student):
    """Compute the student grade for the certificate exercises in a course

    Returns:
        grade (float or None): returns None if the course does not include any
        'certificate' exercise.
    """
    request = RequestFactory().get('/')
    request.session = {}
    request.user = student

    course = modulestore().get_course(course_id)
    grades = courseware_grades.grade(student, request, course)
    sections_grades = grades['section_breakdown']
    for section in sections_grades:
        if section['label'].lower() in ASSIGNMENT_VALID_SHORT_NAMES:
            return section['percent']
    return None


def get_enrolled_verified_students_count(course_id):
    return get_enrolled_verified_students(course_id).count()

def get_enrolled_verified_students(course_id):
    return User.objects.filter(courseenrollment__course_id=course_id).order_by('username')
    """Queryset of active users enrolled in course"""
    return User.objects.filter(
        is_active=True,
        courseenrollment__course_id=course_id,
        courseenrollment__is_active=True,
        courseenrollment__mode__in=CourseMode.VERIFIED_MODES,
    ).order_by('username')

def get_verified_student_grades(course_id):
    """Compute grades of all verified students for a course

    Returns:
        {
            u'user1': {'grade': 0.5, 'passed': True},
            u'user3': {'grade': 0.0, 'passed': False}
        }
    """
    # TODO what if passing_grade is None? (because undefined)
    passing_grade = Course.objects.get(key=course_id).certificate_passing_grade

    student_grades = {}
    for student in get_enrolled_verified_students(course_id):
        grade = get_student_certificate_grade(course_id, student)
        student_grades[student.username] = {
            'passed': grade >= passing_grade if grade else False,
            'grade': grade,
        }
    return student_grades
