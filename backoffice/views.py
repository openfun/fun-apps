# -*- coding: utf-8 -*-

from collections import defaultdict
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from pure_pagination import Paginator, PageNotAnInteger

from bulk_email.models import Optout
from certificates.models import GeneratedCertificate, CertificateStatuses
from edxmako.shortcuts import render_to_string
from microsite_configuration import microsite
from student.models import CourseEnrollment, CourseAccessRole, UserStanding, UserProfile, Registration

from xmodule_django.models import CourseKeyField

from fun_certificates.generator import CertificateInfo
from newsfeed.models import Article

from .certificate_manager.utils import (
    get_certificate_params,
    make_certificate_hash_key,
    make_certificate_filename,
    set_certificate_filename,
)
from .forms import SearchUserForm, UserForm, UserProfileForm, ArticleForm
from .utils import get_course, group_required, get_course_key


ABOUT_SECTION_FIELDS = ['effort', 'video']

logger = logging.getLogger(__name__)

LIMIT_BY_PAGE = 100


def order_and_paginate_queryset(request, queryset, default_order):
    order = request.GET.get('order', default_order)
    direction = '-' if 'd' in request.GET else ''
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
    user_profiles = UserProfile.objects
    if settings.FEATURES['USE_MICROSITES']:
        user_profiles = user_profiles.filter(user__usersignupsource__site=microsite.get_value('SITE_NAME'))
    total_count = user_profiles.count()

    user_profiles = user_profiles.select_related('user')
    if form.data and form.is_valid():
        pattern = form.cleaned_data['search']
        user_profiles = user_profiles.filter(
            Q(user__username__icontains=pattern)
            | Q(user__email__icontains=pattern)
            | Q(name__icontains=pattern)
        )
    user_profiles = order_and_paginate_queryset(request, user_profiles, 'user__username')

    return render(request, 'backoffice/users.html', {
        'user_profiles': user_profiles,
        'search_results_count': user_profiles.paginator.count,
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
    course_id = get_course_key(request.POST['course-id'])
    generated_certificate = GeneratedCertificate.objects.get(user=user, course_id=course_id)
    try:
        new_grade = float(request.POST['new-grade'])
    except ValueError:
        messages.error(request, _(u"Invalid certificate grade."))
        return
    else:
        if not 0 <= new_grade <= 1:
            messages.error(request, _(u"Grades range from 0 to 1."))
        else:
            generated_certificate.grade = request.POST['new-grade']
            generated_certificate.save()
            logger.info(u"Grade change: new grade: %d student: %s course: %s user: %s",
                    new_grade, user.username, course_id, request.user.username)
            messages.success(request, _(u"User grade changed."))

    if 'regenerate' in request.POST:
        # Regenerate PDF and attach to already existing GeneratedCertificate,
        # then force state to 'downloadable'.

        regenerate_certificate(course_id, user, generated_certificate)
        messages.success(request, _(u"Certificate was regenerated"))
        logger.info(u"Certificate regeneration: new grade: %d student: %s course: %s user: %s",
                new_grade, user.username, course_id, request.user.username)


def regenerate_certificate(course_id, user, certificate):
    """Generate or Regenerate PDF and attach to already existing GeneratedCertificate,
    then force state to 'downloadable'.
    """

    (
        course_display_name,
        university,
        teachers, certificate_language
    ) = get_certificate_params(course_id)

    if certificate.status != CertificateStatuses.downloadable:
        certificate.key = make_certificate_hash_key()

    certificate_filename = make_certificate_filename(course_id, key=certificate.key)
    CertificateInfo(
        user.get_profile().name, course_display_name,
        university,
        certificate_filename, teachers, language=certificate_language
    ).generate()
    set_certificate_filename(certificate, certificate_filename)
    certificate.save()


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
    logger.warning(u"Activation email has been resent to user %s at addresse: %s",
            user.username, user.email)
    messages.success(request,
            _(u"Activation email has been resent to user {username} at addresse: {email}".format(
            username=user.username, email=user.email)))


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
        enrollments.append((title, unicode(enrollment.course_id), optout, course_roles))
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
def impersonate_user(request, username):
    user = get_object_or_404(User, username=username, is_superuser=False, is_active=True)

    # We need to define the backend that was used to authenticate the user.
    # This is a bit dirty; a possible workaround would be to add an
    # authentication backend to the platform or to define user.backend as in
    # the django.contrib.auth.authenticate function.
    user.backend = None
    login(request, user)
    return redirect('/')


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
        search_query = {
            'id': news_id
        }
        if settings.FEATURES['USE_MICROSITES']:
            search_query['microsite'] = microsite.get_value('SITE_NAME')
        article = get_object_or_404(Article, **search_query)
    else:
        article = None

    if request.method == 'POST':
        form = ArticleForm(data=request.POST, files=request.FILES, instance=article)
        if form.is_valid():
            form.save()
            if article is None:
                return redirect('backoffice:news-detail', news_id=form.instance.id)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'backoffice/article.html', {
        'form': form,
        'tab': 'news',
    })
