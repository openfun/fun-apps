from opaque_keys.edx.keys import CourseKey
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from openedx.core.lib.api.permissions import ApiKeyHeaderPermission
from courseware import courses
from courseware.grades import grade

def _computed_passed(grade_cutoffs, percent):
    """
    Computes and returns whether the given percent value
    is a passing grade according to the given grade cutoffs.
    """
    nonzero_cutoffs = [cutoff for cutoff in grade_cutoffs.values() if cutoff > 0]
    success_cutoff = min(nonzero_cutoffs) if nonzero_cutoffs else None
    return True if success_cutoff and (percent >= success_cutoff) else False

@transaction.non_atomic_requests
@api_view(['GET'])
@permission_classes([ApiKeyHeaderPermission])
def get_student_course_grade(request, course_key_string, username):
    """
    A server to server api view which computes and returns the student's grade for
    a course. A boolean `passed` property is computed and bound to the grade summary
    dict to know if student has passed or not the course according to the course grade
    cutoffs.

    Example of response :
    {
        "section_breakdown": [
            {
                "category": "Exams",
                "percent": 1.0,
                "detail": "Exams 1 - First section - 100% (1/1)",
                "label": "Exam 01"
            },
        ],
        "passed": true,
        "grade": "A",
        "totaled_scores": {
            "Exams": [[1.0, 1.0, true, "First section", null]],
        },
        "percent": 1.0,
        "grade_breakdown": [
            {
                "category": "Exams",
                "percent": 1.0,
                "detail": "Exams = 100.00% of a possible 100.00%"
            },
        ]
    }
    """

    try:
        student = User.objects.get(username=username)
        course_key = CourseKey.from_string(course_key_string)
        course = courses.get_course(course_key)
    except (User.DoesNotExist, ValueError) as error:
        return Response(str(error), status=404)

    grade_summary = grade(student, request, course, keep_raw_scores=False)
    grade_summary.update({'passed':_computed_passed(course.grade_cutoffs, grade_summary.get('percent'))})

    return Response(grade_summary, status=200)
