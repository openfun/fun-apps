# -*- coding: utf-8 -*-
from collections import namedtuple
import datetime
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect
from django.utils.translation import ugettext, ugettext_lazy as _
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from courses.models import Course, CourseUniversityRelation
from courses.utils import get_about_section
from courseware.courses import course_image_url, get_cms_course_link
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole, User
from universities.models import University
from xmodule.modulestore.django import modulestore

from fun.utils import funwiki as wiki_utils
from fun.utils.export_data import csv_response

from ..certificate_manager.verified import get_verified_student_grades, get_enrolled_verified_students
from ..utils import get_course, group_required, get_course_modes, get_enrollment_mode_count
from ..utils_proctorU_api import get_reports_from_interval

logger = logging.getLogger(__name__)

try:
    INSTALLED_PU = True
    from proctoru.models import ProctoruUser
except ImportError:
    logger.info("ProcotorU XBlock not installed")
    INSTALLED_PU = False


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
        course_infos = get_filtered_course_infos(search_pattern=search_pattern)

    return render(request, 'backoffice/courses/list.html', {
        'course_infos': course_infos,
        'pattern': search_pattern,
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
    course_info = get_course_infos([course])[0]
    User.objects.select_related('profile')
    users = User.objects.filter(courseenrollment__course_id=course.id,
                                 courseenrollment__is_active=True).select_related('profile').order_by('username')

    search_pattern = request.GET.get('search')
    if  search_pattern:
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
def users_without_proctoru_reservation(request, course_key_string):
        if not INSTALLED_PU:
            return HttpResponse('ProctorU xblock not installed')

        if request.method == 'POST':  # export as CSV
            course = get_course(course_key_string)

            verified_students = get_enrolled_verified_students(course.id).select_related("profile")
            proctoru_registered_user = ProctoruUser.objects.filter(student__in=verified_students)
            students_registered_in_proctoru = User.objects.filter(proctoruuser__in=proctoru_registered_user)

            # TODO : not the best way to get students without reservations :
            #  * inscriptions in proctoru model is not bound to course (false negative)
            #  * we can't spot people who registered and cancelled their reservation
            # Thus we can fail to spot some people without reservations
            enrolled_students_not_proctoru = set(verified_students) - set(students_registered_in_proctoru)

            header = ("Name", "Username", "Email")
            rows = [(s.profile.name, s.username, s.email) for s in enrolled_students_not_proctoru]
            course_code = "{}_{}_{}".format(course.id.org, course.id.course, course.id.run)
            filename = 'export-verified-users-without-PU-reservations-{course}-{date}'.format(
                date=datetime.datetime.now().strftime('%Y-%m-%d'),
                course=course_code)

            response = csv_response(header, rows, filename)
            return response


@group_required('fun_backoffice')
def verified(request, course_key_string, action=None):

    course = get_course(course_key_string)
    course_info = get_course_infos([course])[0]

    students_grades = get_verified_student_grades(course.id)

    today = datetime.datetime.today()
    begin = today - datetime.timedelta(100)

    registered_users = get_reports_from_interval(course.id.course, course.id.run, begin)

    if "error" in registered_users:
        return render(request, 'backoffice/courses/verified_error.html', {
            'tab': 'courses',
            'subtab': 'verified',
            'course_key_string': course_key_string,
            'course_info': course_info,
            'error': registered_users["error"],
            "warn": False,
        })

    if "warn" in registered_users:
        return render(request, 'backoffice/courses/verified_error.html', {
            'tab': 'courses',
            'subtab': 'verified',
            'course_key_string': course_key_string,
            'course_info': course_info,
            "error": False,
            'warn': True,
            "course_id": registered_users["warn"]["id"],
            "date_start": registered_users["warn"]["start"],
            "date_end": registered_users["warn"]["end"],
        })

    return render(request, 'backoffice/courses/verified.html', {
            'course_key_string': course_key_string,
            'course_info': course_info,
            'students': registered_users,
            'tab': 'courses',
            'subtab': 'verified',
        })


@group_required('fun_backoffice')
def wiki(request, course_key_string, action=None):
    course = get_course(course_key_string)
    course_info = get_course_infos([course])[0]

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
    course_infos = get_course_infos(courses)

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
    course_infos = get_course_infos([course])[0]
    course_infos.update(get_about_sections(course))
    return CompleteFunCourse(**course_infos)


def get_course_infos(course_descriptors):
    course_modes = get_course_modes()
    course_descriptor_ids = [course_descriptor.id for course_descriptor in course_descriptors]
    courses = Course.objects.filter(key__in=course_descriptor_ids)
    course_enrollment_counts = get_course_enrollment_counts(course_descriptor_ids)
    course_dict = {course.key: course for course in courses}
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

def get_course_enrollment_counts(course_descriptors_ids):
    queryset = (
        CourseEnrollment.objects
        .filter(course_id__in=course_descriptors_ids)
        .values('course_id')
        .annotate(total=Count('course_id'))
        .order_by()
     )
    return {
        result['course_id']: result['total'] for result in queryset
    }

def format_datetime(dt):
    FORMAT = '%Y-%m-%d %H:%M'
    return dt.strftime(FORMAT) if dt else ''

# def create_csv(csv_header, filename, rows):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=%s' % filename
#     writer = csv.writer(response)
#     writer.writerow([field.encode('utf-8') for field in csv_header])
#
#     for row in rows:
#         row_converted = []
#         for s in row:
#             try:
#                 row_converted.append(s.encode("utf8"))
#             except AttributeError:
#                 row_converted.append(u"{}".format(s))
#
#         writer.writerow(row_converted)
#
#     return response, writer
