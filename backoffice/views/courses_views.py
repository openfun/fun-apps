# -*- coding: utf-8 -*-
from collections import namedtuple
import datetime
import logging
import re

from django.core.cache import cache
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _
from django.views.decorators.http import require_POST
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course, CourseUniversityRelation
from courses.utils import get_about_section
from courseware.courses import get_cms_course_link

from opaque_keys.edx.keys import CourseKey
from openedx.core.lib.courses import course_image_url
from student.models import CourseEnrollment, CourseAccessRole, User

from universities.models import University
from xmodule.modulestore.django import modulestore

from courses.models import Course
from fun.utils import funwiki as wiki_utils
from fun.utils.export_data import csv_response

from ..certificate_manager.verified import get_verified_student_grades, get_enrolled_verified_students
from ..utils import get_course, group_required, get_course_modes, get_enrollment_mode_count

logger = logging.getLogger(__name__)


COURSE_FIELDS = [
    'course',
    'fun',
    'course_image_url',
    'students_count',
    'title',
    'university',

    'url',
    'studio_url',
    'modes',
]
ABOUT_SECTION_FIELDS = ['effort', 'video']
FunCourse = namedtuple('FunCourse', COURSE_FIELDS)
CompleteFunCourse = namedtuple('CompleteFunCourse', COURSE_FIELDS + ABOUT_SECTION_FIELDS)


@group_required('fun_backoffice')
def courses_list(request):
    if request.method == 'POST':  # export as CSV
        csv_header = [ugettext(u"Title"), ugettext(u"University"), ugettext(u"Organisation code"),
                ugettext(u"Course"), ugettext(u"Run"), ugettext(u"Start date"), ugettext(u"End date"),
                ugettext(u"Enrollment start"), ugettext(u"Enrollment end"), ugettext(u"Students count"),
                ugettext(u"Effort"), ugettext(u"Image"), ugettext(u"Video"), ugettext(u"Url")]

        filename = 'export-cours-%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d')
        course_infos = get_complete_courses_info()

        rows = [
            (ci.title, ci.university, ci.course.id.org, ci.course.id.course, ci.course.id.run,
             format_datetime(ci.course.start), format_datetime(ci.course.end),
             format_datetime(ci.course.enrollment_start), format_datetime(ci.course.enrollment_end),
             ci.students_count, ci.effort,' https://%s%s' % (settings.LMS_BASE, ci.course_image_url), ci.video, ci.url
             )
            for ci in course_infos
        ]

        response = csv_response(csv_header, rows, filename)

        return response
    else:
        search_pattern = request.GET.get('search')
        course_infos = Course.objects.values()


        if search_pattern:
            course_infos = course_infos.filter(
                Q(title__icontains=search_pattern) |
                Q(key__icontains=search_pattern) |
                Q(university_display_name__icontains=search_pattern)
            )
        enrollments = get_course_enrollment_counts(course_infos)

        for course in course_infos:
            course["course_enrollments"] = enrollments[course["key"]]

    return render(request, 'backoffice/courses/list.html', {
        'course_infos': course_infos,
        'pattern': search_pattern,
        'lms_base': settings.LMS_BASE,
        'tab': 'courses',
    })


@group_required('fun_backoffice')
def course_detail(request, course_key_string):
    """Course is deleted from Mongo and staff and students enrollments from mySQL.
    States and responses from students are not yet deleted from mySQL
    (StudentModule, StudentModuleHistory are very big tables)."""

    ck = CourseKey.from_string(course_key_string)
    course = get_course(course_key_string)
    if course is None:
        raise Http404
    mode_count = get_enrollment_mode_count(ck)
    course_info = get_complete_course_info(course)
    funcourse, _created = Course.objects.get_or_create(key=ck)

    try:
        university = University.objects.get(code=ck.org)
    except University.DoesNotExist:
        messages.warning(request, _(u"University with code <strong>%s</strong> does not exist.") % ck.org)
        university = None
    if university and university not in funcourse.universities.all():
        CourseUniversityRelation.objects.create(course=funcourse, university=university)

    if request.method == 'POST':
        if request.POST['action'] == 'delete-course':
            # from xmodule.contentstore.utils.delete_course_and_groups function
            module_store = modulestore()
            with module_store.bulk_operations(ck):
                module_store.delete_course(ck, request.user.id)

            CourseAccessRole.objects.filter(course_id=ck).delete()  # shall we also delete student's enrollments ?
            funcourse.delete()
            messages.warning(request, _(u"Course <strong>%s</strong> has been deleted.") % course_info.course.id)
            logger.warning('Course %s deleted by user %s', course_info.course.id, request.user.username)
            return redirect('backoffice:courses-list')

    try:
        university = University.objects.get(code=course_info.course.org)
    except University.DoesNotExist:
        university = None

    roles = CourseAccessRole.objects.filter(course_id=ck)

    return render(request, 'backoffice/courses/detail.html', {
            'course_info': course_info,
            'university': university,
            'roles': roles,
            'mode_count': mode_count,
            'tab': 'courses',
            'subtab': 'home',
        })


@group_required('fun_backoffice')
def enrolled_users(request, course_key_string):
    course = get_course(course_key_string)
    course_info = get_course_infos_or_404([course])[0]
    User.objects.select_related('profile')
    users = User.objects.filter(courseenrollment__course_id=course.id,
                                courseenrollment__is_active=True).select_related('profile').order_by('username')

    search_pattern = request.GET.get('search')
    if search_pattern:
        users = users.filter(Q(username__icontains=search_pattern) |
                             Q(email__icontains=search_pattern) |
                             Q(profile__name__icontains=search_pattern))

    if request.method == 'POST':  # export as CSV
        course_code = "{}_{}_{}".format(course.id.org, course.id.course, course.id.run)
        filename = 'export-email-usernames-{course}-{date}'.format(date=datetime.datetime.now().strftime('%Y-%m-%d'),
                                                                   course=course_code)
        if search_pattern:
            filename += "-search_{}".format(search_pattern)
        filename += ".csv"

        csv_header = [ugettext(u"Username"), ugettext(u"Name"), ugettext(u"Email")]
        rows = [(u.username, u.profile.name, u.email) for u in users]
        response = csv_response(csv_header, rows, filename)

        return response
    else:
        paginator = Paginator(users, request=request, per_page=100)
        try:
            users = paginator.page(request.GET.get('page', 1))
        except PageNotAnInteger:
            users = paginator.page(1)
        except EmptyPage:
            users = paginator.page(paginator.num_pages)

        return render(request, 'backoffice/courses/users.html', {
            'course_key_string': course_key_string,
            'course_info': course_info,
            'tab': 'courses',
            'subtab': 'users',
            'users': users,
            'search': search_pattern
        })


@group_required('fun_backoffice')
def wiki(request, course_key_string, action=None):
    course = get_course(course_key_string)
    course_info = get_course_infos_or_404([course])[0]

    base_page = wiki_utils.get_base_page(course)

    if request.method == 'POST':
        value, word = {'open': (True, _(u"opened")), 'close': (False, _(u"closed"))}[request.POST['action']]
        result = wiki_utils.set_permissions(course, value)
        if result:
            messages.success(request, _(u"Wiki was successfully ") + unicode(word))
        else:
            messages.error(request, _(u"Wiki could not be ") + unicode(word))

        return redirect(reverse('backoffice:course-wiki', args=[course_key_string]))

    pages = wiki_utils.get_page_tree([base_page])
    html = _(u"This course has no wiki")
    if any(pages):
        pages, html = wiki_utils.render_html_tree(pages, '')

    return render(request, 'backoffice/courses/wiki.html', {
            'course_key_string': course_key_string,
            'course_info': course_info,
            'pages': pages,
            'html': html,
            'tab': 'courses',
            'subtab': 'wiki',
        })


def get_filtered_course_infos(search_pattern=None):
    courses = get_sorted_courses()
    course_infos = get_course_infos_or_404(courses)

    if search_pattern:
        course_infos = [course for course in course_infos
                        if search_pattern in course['title']
                        or search_pattern in course['course'].id.to_deprecated_string()]

    return course_infos


def get_complete_courses_info():
    return [get_complete_course_info(course) for course in get_sorted_courses()]


def get_sorted_courses():
    courses = modulestore().get_courses()
    courses = sorted(courses, key=lambda course: course.number)
    return courses


def get_complete_course_info(course):
    """Complete course info for displaying the details of a course.

    Returns:
        CompleteFunCourse
    """
    course_infos = get_course_infos_or_404([course])[0]
    course_infos.update(get_about_sections(course))
    return CompleteFunCourse(**course_infos)


def get_course_infos_or_404(course_descriptors):
    if not course_descriptors:
        pass
    elif all([descriptor is None for descriptor in course_descriptors]):
        raise Http404

    course_modes = get_course_modes()
    course_descriptor_ids = [course_descriptor.id for course_descriptor in course_descriptors]
    courses = Course.objects.filter(key__in=course_descriptor_ids).values()
    course_enrollment_counts = get_course_enrollment_counts(courses)
    course_dict = {course["key"]: course for course in courses}
    return [
        get_course_info(
            course_descriptor,
            course_dict.get(course_descriptor.id.to_deprecated_string()),
            course_enrollment_counts.get(course_descriptor.id.to_deprecated_string(), 0),
            course_modes,
        )
        for course_descriptor in course_descriptors
    ]

def get_about_sections(course_descriptor):
    about_sections = {
        field: get_about_section(course_descriptor, field) or ''
        for field in ABOUT_SECTION_FIELDS
    }
    about_sections['effort'] = about_sections['effort'].replace('\n', '')  # clean the many CRs
    if about_sections['video']:
        try:  # edX stores the Youtube iframe HTML code, let's extract the Dailymotion Cloud ID
            about_sections['video'] = re.findall(r'www.youtube.com/embed/(?P<hash>[\w]+)\?', about_sections['video'])[0]
        except IndexError:
            pass
    return about_sections

def get_course_info(course_descriptor, course, students_count, course_modes):
    """Returns a dict containing original edX course and some complementary properties."""
    return {
        'course': course_descriptor,
        'fun': course,
        'course_image_url': course_image_url(course_descriptor),
        'students_count': students_count,
        'title': course_descriptor.display_name_with_default,
        'university': course_descriptor.display_org_with_default,
        'url': 'https://%s%s' % (
            settings.LMS_BASE,
            reverse('about_course', args=[course_descriptor.id.to_deprecated_string()])
        ),
        'studio_url': get_cms_course_link(course_descriptor),
        'modes': course_modes[unicode(course_descriptor.id)] if course_modes else [],
    }


def get_course_enrollment_counts(courses):
    """
    Count and cache course enrollments for a list of courses.
    Cache timeout will be set short or long depending on wether
    course enrollment is in progress or has been completed
    or not yet begun.


    courses: list of course keys as strings
    returns: a dict which keys are course keys and values count
    of enrollments
    """
    short_timeout = 60 * 5  # five minutes
    long_timeout = 60 * 60 * 24  # one day
    result = {}
    course_descriptors_ids = []

    # Retrieve from cache available course enrollment counts
    for idx, course in enumerate(courses):
        count = cache.get(course["key"])
        if count:
            result[course["key"]] = count
        else:
            course_descriptors_ids.append(
                CourseKey.from_string(course["key"])
            )

    # Get others from bdd
    if course_descriptors_ids:
        queryset = (
            CourseEnrollment.objects
            .filter(course_id__in=course_descriptors_ids)
            .values('course_id')
            .annotate(total=Count('course_id'))
            .order_by()
        )
        # Cache new results
        now = datetime.datetime.now()
        for course in queryset:
            result[course["course_id"]] = course['total']
            # Find course enrollment end date and set cache timeout
            for c in courses:
                if c["key"] == course["course_id"]:
                    if (c.get("enrollement_end_date") and
                        c["enrollement_end_date"] > now):
                        timeout = short_timeout
                    else:
                        timeout = long_timeout
                    break

            cache.set(
                course["course_id"],
                course['total'],
                timeout
            )

    return result


def format_datetime(dt):
    FORMAT = '%Y-%m-%d %H:%M'
    return dt.strftime(FORMAT) if dt else ''
