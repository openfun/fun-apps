# -*- coding: utf-8 -*-

import csv
from collections import namedtuple, defaultdict
import datetime
import logging
import re

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.shortcuts import render, redirect
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _

from pure_pagination import Paginator, PageNotAnInteger

from bulk_email.models import Optout
from certificates.models import GeneratedCertificate
from courseware.courses import course_image_url, get_courses, get_cms_course_link
from edxmako.shortcuts import render_to_string
from microsite_configuration import microsite
from opaque_keys.edx.keys import CourseKey
from student.models import CourseEnrollment, CourseAccessRole, UserStanding, Registration

from xmodule_django.models import CourseKeyField
from xmodule.modulestore.django import modulestore

from newsfeed.models import Article
from universities.models import University

from .forms import SearchUserForm, UserForm, UserProfileForm, ArticleForm
from .utils import get_course, group_required, get_course_key
from courses.models import Course, CourseUniversityRelation
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

LIMIT_BY_PAGE = 100


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
            row = [
                course_info.title.encode('utf-8'),
                course_info.university.encode('utf-8'),
                course_info.course.id.org.encode('utf-8'),
                course_info.course.id.course.encode('utf-8'),
                course_info.course.id.run.encode('utf-8'),
                format_datetime(course_info.course.start),
                format_datetime(course_info.course.end),
                format_datetime(course_info.course.enrollment_start),
                format_datetime(course_info.course.enrollment_end),
                course_info.students_count,
                course_info.effort.encode('utf-8'),
                'https://%s%s' % (
                    settings.LMS_BASE,
                    course_info.course_image_url.encode("utf-8")
                ),
                course_info.video,
                course_info.url
            ]
            writer.writerow(row)
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

    return render(request, 'backoffice/course.html', {
            'course_info': course_info,
            'university': university,
            'roles': roles,
            'tab': 'courses',
        })


def order_and_paginate_queryset(request, queryset, default_order):
    order = request.GET.get('order', default_order)
    direction = '' if 'd' in request.GET else '-'
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1
    queryset = queryset.order_by(direction + order)
    paginator = Paginator(queryset, LIMIT_BY_PAGE, request=request)
    return paginator.page(page)


@group_required('fun_backoffice')
def user_list(request):
    form = SearchUserForm(data=request.GET)
    users = User.objects.select_related('profile').exclude(profile__isnull=True)
    if settings.FEATURES['USE_MICROSITES']:
        users = users.filter(usersignupsource__site=microsite.get_value('SITE_NAME'))
    total_count = users.count()

    if form.data and form.is_valid():
        pattern = form.cleaned_data['search']
        users = users.filter(
            Q(username__icontains=pattern)
            | Q(email__icontains=pattern)
            | Q(profile__name__icontains=pattern)
        )
    users = order_and_paginate_queryset(request, users, 'date_joined')

    return render(request, 'backoffice/users.html', {
        'users': users,
        'total_count': total_count,
        'form': form,
        'tab': 'users',
    })


def ban_user(request, user):
    user_account, _created = UserStanding.objects.get_or_create(
        user=user, defaults={'changed_by': request.user})
    if request.POST['value'] == 'disable':
        user_account.account_status = UserStanding.ACCOUNT_DISABLED
        messages.success(request, _(u"Successfully disabled {}'s account").format(user.username))
    elif request.POST['value'] == 'reenable':
        user_account.account_status = UserStanding.ACCOUNT_ENABLED
        messages.success(request, _(u"Successfully reenabled {}'s account").format(user.username))
    user_account.changed_by = request.user
    user_account.standing_last_changed_at = timezone.now()
    user_account.save()

def change_password(request, user):
    user.set_password(request.POST['new-password'])
    user.save()
    messages.success(request, _(u"User password changed"))

def change_grade(request, user):
    """ Change a certificate grade per user, per course.

    Grade comes as string and needs to range from 0 to 1.
    Args:
         request (HttpRequest): Contains the course id in request.POST['course-id'].
         user (User): The user attached to the certificate.
     """
    course = get_course_key(request.POST['course-id'])
    generated_certificate = GeneratedCertificate.objects.get(user=user, course_id=course)
    try:
        new_grade = float(request.POST['new-grade'])
    except ValueError:
        messages.error(request, _(u"Invalid certificate grade."))
    else:
        if not 0 <= new_grade <= 1:
            messages.error(request, _(u"Grades range from 0 to 1."))
        else:
            generated_certificate.grade = request.POST['new-grade']
            generated_certificate.save()
            messages.success(request, _(u"User grade changed."))


def resend_activation_email(request, user):

    context = {
        'name': user.profile.name,
        'key': Registration.objects.get(user=user).activation_key,
        'site': microsite.get_value('SITE_NAME', settings.SITE_NAME)
    }
    subject = ''.join(render_to_string('emails/activation_email_subject.txt', context).splitlines())
    message = render_to_string('emails/activation_email.txt', context)

    from_address = microsite.get_value(
        'email_from_address',
        settings.DEFAULT_FROM_EMAIL
    )
    user.email_user(subject, message, from_address)
    logger.warning(u"Activation email has been resent to user %s at addresse: %s", user.username, user.email)
    messages.success(
        request,
        _(u"Activation email has been resent to user %s at addresse: %s") % (user.username, user.email)
    )


user_actions = {'ban-user' : ban_user,
                'change-password' : change_password,
                'change-grade' : change_grade,
                'resend-activation': resend_activation_email,
                }

@group_required('fun_backoffice')
def user_detail(request, username):
    if settings.FEATURES['USE_MICROSITES']:
        users = User.objects.filter(usersignupsource__site=microsite.get_value('SITE_NAME'))
    else:
        users = User.objects.all()
    try:
        user = users.select_related('profile').get(username=username)
    except User.DoesNotExist:
        raise Http404()

    if 'action' in request.POST:
        action = request.POST.get('action')
        if action in user_actions:
            user_actions[action](request, user)
        else:
            messages.error(request, _(u"Invalid user action."))
        return redirect('backoffice:user-detail', username=username)

    certificates = GeneratedCertificate.objects.filter(user=user)

    userform = UserForm(instance=user, data=request.POST or None)
    userprofileform = UserProfileForm(instance=user.profile, data=request.POST or None)

    disabled = UserStanding.objects.filter(user=user,
                                           account_status=UserStanding.ACCOUNT_DISABLED)

    enrollments = []
    optouts = Optout.objects.filter(user=user).values_list('course_id', flat=True)
    user_roles = defaultdict(list)
    for car in CourseAccessRole.objects.filter(user=user).exclude(course_id=CourseKeyField.Empty):
        user_roles[unicode(car.course_id)].append(car.role)

    for enrollment in CourseEnrollment.objects.filter(user=user):
        key = unicode(enrollment.course_id)
        optout = key in optouts
        course = get_course(key)
        if not course:
            continue  # enrollment can exists for course that does not exist anymore in mongo
        title = course.display_name
        course_roles = user_roles.get(key, [])
        enrollments.append((title, enrollment.course_id, optout, course_roles))

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
        'certificates' : certificates
        })


@group_required('fun_backoffice')
def news_list(request):
    articles = Article.objects.all().order_by('-created_at')
    if settings.FEATURES['USE_MICROSITES']:
        articles = articles.filter(microsite=microsite.get_value('SITE_NAME'))

    articles = order_and_paginate_queryset(request, articles, 'created_at')

    return render(request, 'backoffice/articles.html', {
        'articles': articles,
        'tab': 'news',
    })


@group_required('fun_backoffice')
def news_detail(request, news_id=None):
    if news_id:
        article = Article.objects.get(id=news_id)
        if settings.FEATURES['USE_MICROSITES']:
            assert article.microsite == microsite.get_value('SITE_NAME')
    else:
        article = None

    form = ArticleForm(data=request.POST or None, instance=article)
    if form.is_valid():
        form.save()
        return redirect('backoffice:news-list')

    return render(request, 'backoffice/article.html', {
        'form': form,
        'tab': 'news',
    })
