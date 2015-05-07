# -*- coding: utf-8 -*-

import csv
from collections import namedtuple
import datetime
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.forms.models import inlineformset_factory
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

from bulk_email.models import Optout
from courseware.courses import course_image_url, get_courses, get_cms_course_link
from courseware.courses import course_image_url, get_course_about_section, get_courses, get_cms_course_link
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole, UserProfile, UserStanding
from xmodule.modulestore.django import modulestore

from universities.models import University

from .forms import FirstRequiredFormSet, SearchUserForm, UserForm, UserProfileForm
from .models import Course, Teacher
from .utils import get_course, group_required
from courses.utils import get_about_section

ABOUT_SECTION_FIELDS = ['effort', 'video']

logger = logging.getLogger(__name__)

FunCourse = namedtuple('FunCourse', [
    'course',
    'fun',
    'course_image_url',
    'students_count',
    'title',
    'university',
    'url',
    'studio_url'
] + ABOUT_SECTION_FIELDS)

LIMIT_SEARCH_RESULT = 100


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

def get_course_info(course_descriptor, course, students_count):
    """Returns an object containing original edX course and some complementary properties."""
    about_sections = get_about_sections(course_descriptor)
    course_info = FunCourse(
        course=course_descriptor,
        fun=course,
        course_image_url=course_image_url(course_descriptor),
        students_count=students_count,
        title=course_descriptor.display_name_with_default,
        university=course_descriptor.display_org_with_default,
        url='https://%s%s' % (settings.LMS_BASE,
                reverse('about_course', args=[course_descriptor.id.to_deprecated_string()])),
        studio_url=get_cms_course_link(course_descriptor),
        **about_sections
    )
    return course_info

def get_course_enrollment_counts(course_descriptors_ids):
    queryset = (
        CourseEnrollment.objects
        .filter(course_id__in=course_descriptors_ids)
        .values('course_id')
        .annotate(total=Count('course_id'))
     )
    return {
        result['course_id']: result['total'] for result in queryset
    }

def get_course_infos(course_descriptors):
    course_descriptor_ids = [course_descriptor.id for course_descriptor in course_descriptors]
    courses = Course.objects.filter(key__in=course_descriptor_ids)
    course_enrollment_counts = get_course_enrollment_counts(course_descriptor_ids)
    course_dict = {course.key: course for course in courses}
    return [
        get_course_info(
            course_descriptor,
            course_dict.get(course_descriptor.id.to_deprecated_string()),
            course_enrollment_counts.get(course_descriptor.id.to_deprecated_string(), 0)
        )
        for course_descriptor in course_descriptors
    ]

def get_complete_course_info(course_descriptor):
    return get_course_infos([course_descriptor])[0]

def get_filtered_course_infos(request):
    course_infos = get_course_infos(get_courses(request.user))
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
            writer.writerow([
                course_info.title.encode('utf-8'),
                course_info.university.encode('utf-8'),
                course_info.course.id.org,
                course_info.course.id.course,
                course_info.course.id.run,
                format_datetime(course_info.course.start),
                format_datetime(course_info.course.end),
                format_datetime(course_info.course.enrollment_start),
                format_datetime(course_info.course.enrollment_end),
                course_info.students_count,
                course_info.effort.encode('utf-8'),
                'https://%s%s' % (settings.LMS_BASE, course_info.course_image_url),
                course_info.video,
                course_info.url
            ])

        return response

    return render(request, 'backoffice/courses.html', {
        'course_infos': course_infos,
        'pattern': pattern,
        'tab': 'courses',
    })


@group_required('fun_backoffice')
def course_detail(request, course_key_string):
    """Course is deleted from Mongo and staff and students enrollments from mySQL.
    States and responses from students are not yet deleted from mySQL
    (StudentModule, StudentModuleHistory are very big tables)."""

    course_info = get_complete_course_info(get_course(course_key_string))
    ck = CourseKey.from_string(course_key_string)
    funcourse, _created = Course.objects.get_or_create(key=ck)
    if not funcourse.university:
        try:
            funcourse.university = University.objects.get(code=ck.org)
            funcourse.save()
        except University.DoesNotExist:
            messages.warning(request, _(u"University with code <strong>%s</strong> does not exist.") % ck.org)
    TeacherFormSet = inlineformset_factory(Course, Teacher,
                                           formset=FirstRequiredFormSet,
                                           can_delete=True, max_num=4, extra=4)

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
            'tab': 'courses',
        })


@group_required('fun_backoffice')
def user_list(request):

    form = SearchUserForm(data=request.GET)
    users = User.objects.select_related('profile').exclude(profile__isnull=True).order_by('date_joined')

    total_count = users.count()

    if form.data and form.is_valid():
        pattern = form.cleaned_data['search']
        users = users.filter(Q(username__icontains=pattern)
                | Q(email__icontains=pattern)
                | Q(profile__name__icontains=pattern)
                )
        count = users.count()

    users = users[:LIMIT_SEARCH_RESULT]
    count = users.count()

    return render(request, 'backoffice/users.html', {
        'users': users,
        'count': count,
        'total_count': total_count,
        'form': form,
        'tab': 'users',
        })


@group_required('fun_backoffice')
def user_detail(request, username):
    user = User.objects.select_related('profile').get(username=username)
    if 'action' in request.POST:
        if request.POST['action'] == 'ban-user':
            user_account, created = UserStanding.objects.get_or_create(
                    user=user, defaults={'changed_by': request.user})
            if request.POST['value'] == 'disable':
                user_account.account_status = UserStanding.ACCOUNT_DISABLED
                messages.success(request, _(u"Successfully disabled {}'s account").format(user.username))
            elif request.POST['value'] == 'reenable':
                user_account.account_status = UserStanding.ACCOUNT_ENABLED
                messages.success(request, _(u"Successfully reenabled {}'s account").format(username))
            user_account.changed_by = request.user
            user_account.standing_last_changed_at = timezone.now()
            user_account.save()

        elif request.POST['action'] == 'change-password':
            user.set_password(request.POST['new-password'])
            user.save()
            messages.success(request, _(u"User password changed"))

        return redirect('backoffice:user-list')



    userform = UserForm(instance=user, data=request.POST or None)
    userprofileform = UserProfileForm(instance=user.profile, data=request.POST or None)

    disabled = UserStanding.objects.filter(user=user,
        account_status=UserStanding.ACCOUNT_DISABLED).exists()

    enrollments = []
    for enrollment in CourseEnrollment.objects.filter(user=user):
        optout = Optout.objects.filter(user=user, course_id=enrollment.course_id).exists()
        title = get_course(enrollment.course_id.to_deprecated_string()).display_name
        roles = CourseAccessRole.objects.filter(
                user=user, course_id=enrollment.course_id).values_list('role', flat=True)
        enrollments.append((title, enrollment.course_id, optout, roles))

    if request.method == 'POST':
        if all([userform.is_valid(), userprofileform.is_valid()]):
            userform.save()
            userprofileform.save()
            messages.success(request, _(u"User %s has been modified") % user.username)
            return redirect('backoffice:user-list')

    return render(request, 'backoffice/user.html', {
        'userform': userform,
        'userprofileform': userprofileform,
        'enrollments': enrollments,
        'disabled': disabled,
        'tab': 'users',
        })
