from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import Http404
from bulk_email.models import Optout
from edxmako.shortcuts import render_to_response
from opaque_keys.edx.keys import CourseKey

from fun.utils import get_course

def unsubscribe(request, course_id):
    """
    Create an optout resource related to the user retrieved through the email address
    passed as argument and the current course.
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course(course_id)
    email = request.GET.get('u')
    user = None

    if not course or not email:
        raise Http404


    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Silently pass and display the page as if the un.subscribe succeeded in order
        # to not reveal any existing account
        pass

    if user:
        Optout.objects.get_or_create(user=user, course_id=course_key)

    return render_to_response(
        'mailing_list/index.html', {
            "mode": "unsubscribe",
            "course_title": course.display_name_with_default,
            "email": email,
            "revert_link": "{}?u={}".format(reverse("fun_mailing_list:subscribe", kwargs={"course_id": course_id}), email)
        }
    )

def subscribe(request, course_id):
    """
    Remove the optout resource related to the user retrieved through the email address
    passed as argument and the current course.
    """
    course_key = CourseKey.from_string(course_id)
    course = get_course(course_id)
    email = request.GET.get('u')
    user = None

    if not course or not email:
        raise Http404



    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # Silently pass and display the page as if the un.subscribe succeeded in order
        # to not reveal any existing account
        pass

    if user:
        Optout.objects.filter(user=user, course_id=course_key).delete()

    return render_to_response(
        'mailing_list/index.html', {
            "mode": "subscribe",
            "course_title": course.display_name_with_default,
            "email": email,
            "revert_link": "{}?u={}".format(reverse("fun_mailing_list:unsubscribe", kwargs={"course_id": course_id}), email)
        }
    )
