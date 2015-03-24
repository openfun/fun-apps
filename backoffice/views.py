# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
import datetime
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.utils import IntegrityError
from django.forms.models import inlineformset_factory
from django.shortcuts import render, redirect
from django.utils.translation import ugettext, ugettext_lazy as _

from courseware.courses import course_image_url, get_course_about_section, get_courses, get_cms_course_link
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole
from xmodule.modulestore.django import modulestore

from universities.models import University

from .forms import FirstRequiredFormSet
from .models import Course, Teacher
from .utils import get_course, group_required

ABOUT_SECTION_FIELDS = ['title', 'university', 'effort', 'video']

log = logging.getLogger(__name__)

FunCourse = namedtuple('FunCourse',
        'course, fun, course_image_url, students_count, url, studio_url, ' + ', '.join(ABOUT_SECTION_FIELDS))



def get_course_info(course):
    """Returns an object containing original edX course and some complementary properties."""
    about_sections = {}
    for field in ABOUT_SECTION_FIELDS:
        about_sections[field] = get_course_about_section(course, field)
    about_sections['effort'] = about_sections['effort'].replace('\n', '')  # clean the many CRs
    if about_sections['video']:
        try:  # edX stores the Youtube iframe HTML code, let's extract the Dailymotion Cloud ID
            about_sections['video'] = re.findall('www.youtube.com/embed/(?P<hash>[\w]+)\?', about_sections['video'])[0]
        except IndexError:
            pass
    try:
        funcourse = Course.objects.get(key=course.id)
    except Course.DoesNotExist:
        funcourse = None

    course_info = FunCourse(course=course,
            fun=funcourse,
            course_image_url=course_image_url(course),
            students_count=CourseEnrollment.objects.filter(course_id=course.id).count(),
            url='https://%s%s' % (settings.LMS_BASE,
                    reverse('about_course', args=[course.id.to_deprecated_string()])),
            studio_url=get_cms_course_link(course),
            **about_sections
            )
    return course_info


def get_filtered_course_infos(request):
    course_infos = [get_course_info(course) for course in get_courses(request.user)]
    pattern = request.GET.get('search')

    if pattern:
        course_infos = [course for course in course_infos
                if pattern in course.title
                or pattern in course.course.id.to_deprecated_string()]

    return course_infos, pattern


def format_datetime(dt):
    FORMAT = '%Y-%m-%d %H:%M'
    return dt.strftime(FORMAT) if dt else ''


@group_required('fun_backoffice')
def courses_list(request):
    course_infos, pattern = get_filtered_course_infos(request)

    if request.method == 'POST':
        # export as CSV
        filename = 'export-cours-%s.csv' % datetime.datetime.now().strftime('%Y-%m-%d')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        writer = csv.writer(response)
        csv_header = [ugettext(u"Title"), ugettext(u"University"), ugettext(u"Organisation code"),
                ugettext(u"Course"), ugettext(u"Run"), ugettext(u"Start date"), ugettext(u"End date"),
                ugettext(u"Enrollment start"), ugettext(u"Enrollment end"), ugettext(u"Students count"),
                ugettext(u"Effort"), ugettext(u"Image"), ugettext(u"Video"), ugettext(u"Url")]
        writer.writerow([field.encode('utf-8') for field in csv_header])

        for course_info in course_infos:
            raw = []
            raw.append(course_info.title.encode('utf-8'))
            raw.append(course_info.university.encode('utf-8'))
            raw.append(course_info.course.id.org)
            raw.append(course_info.course.id.course)
            raw.append(course_info.course.id.run)
            raw.append(format_datetime(course_info.course.start))
            raw.append(format_datetime(course_info.course.end))
            raw.append(format_datetime(course_info.course.enrollment_start))
            raw.append(format_datetime(course_info.course.enrollment_end))
            raw.append(course_info.students_count)
            raw.append(course_info.effort.encode('utf-8'))
            raw.append('https://%s%s' % (settings.LMS_BASE, course_info.course_image_url))
            raw.append(course_info.video)
            raw.append(course_info.url)
            writer.writerow(raw)

        return response

    return render(request, 'backoffice/courses.html', {
        'course_infos': course_infos,
        'pattern': pattern,
    })


@group_required('fun_backoffice')
def course_detail(request, course_key_string):
    """Course is deleted from Mongo and staff and students enrollments from mySQL.
    States and responses from students are not yet deleted from mySQL
    (StudentModule, StudentModuleHistory are very big tables)."""

    course_info = get_course_info(get_course(course_key_string))
    ck = CourseKey.from_string(course_key_string)
    try:
        funcourse = Course.objects.create(key=ck)
    except IntegrityError:
        funcourse = Course.objects.get(key=ck)
    if not funcourse.university:
        try:
            funcourse.university = University.objects.get(code=ck.org)
            funcourse.save()
        except University.DoesNotExist:
            messages.warning(request, _(u"University with code <strong>%s</strong> does not exist.") % ck.org)
    TeacherFormSet = inlineformset_factory(Course, Teacher, formset=FirstRequiredFormSet, can_delete=True, max_num=4, extra=4)

    if request.method == 'POST':
        if request.POST['action'] == 'delete-course':
            # from xmodule.contentstore.utils.delete_course_and_groups function
            module_store = modulestore()
            with module_store.bulk_operations(ck):
                module_store.delete_course(ck, request.user.id)

            CourseAccessRole.objects.filter(course_id=ck).delete()  # shall we also delete student's enrollments ?
            funcourse.delete()
            messages.warning(request, _(u"Course <strong>%s</strong> has been deleted.") % course_info.course.id)
            log.warning('Course %s deleted by user %s', course_info.course.id, request.user.username)
            return redirect('backoffice:courses-list')

        elif request.POST['action'] == 'update-teachers':
            teacher_formset = TeacherFormSet(instance=funcourse, data=request.POST or None)
            if teacher_formset.is_valid():
                teacher_formset.save()

                messages.success(request, _(u"Teachers have been updated"))
                return redirect("backoffice:course-detail", course_key_string=course_key_string)

    try:
        university = University.objects.get(code=course_info.course.org)
    except University.DoesNotExist:
        university = None

    teacher_formset = TeacherFormSet(instance=funcourse)
    roles = CourseAccessRole.objects.filter(course_id=ck)

    return render(request, 'backoffice/course.html', {
            'course_info': course_info,
            'teacher_formset': teacher_formset,
            'university': university,
            'roles': roles,

        })
