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

from bulk_email.models import Optout
from certificates.models import GeneratedCertificate, CertificateStatuses
from course_modes.models import CourseMode
from edxmako.shortcuts import render_to_string
from microsite_configuration import microsite
from student.models import CourseEnrollment, CourseAccessRole, UserStanding, UserProfile, Registration

from xmodule_django.models import CourseKeyField

from fun_certificates.generator import CertificateInfo
from payment.models import TermsAndConditions, PAYMENT_TERMS

from ..certificate_manager.utils import (
    get_certificate_params,
    make_certificate_hash_key,
    make_certificate_filename,
    set_certificate_filename,
)
from ..forms import SearchUserForm, UserForm, UserProfileForm
from ..utils import get_course, group_required, get_course_key, order_and_paginate_queryset



logger = logging.getLogger(__name__)



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


def change_course_mode(request, user):
    """Change user enrollment mode to course. honor or verified."""

    course_id = get_course_key(request.POST['course-id'])
    mode = request.POST['course-mode']
    if CourseMode.objects.filter(course_id=course_id, mode_slug=mode).exists():
        update = CourseEnrollment.objects.filter(user=user, course_id=course_id
                ).update(mode=mode)
        if update == 1:
            messages.success(request, _(u"User's course enrollment for <strong>%s</strong> has been set to <strong>%s</strong>") % (
                course_id, mode))
            logger.warning(u"User %s CourseMode for course %s set to %s",
                user.username, course_id, mode)



user_actions = {'ban-user': ban_user,
                'change-password': change_password,
                'change-grade': change_grade,
                'resend-activation': resend_activation_email,
                'change-mode': change_course_mode,
                }


def get_accepted_payment_terms(user):
    accepted = TermsAndConditions.version_accepted(PAYMENT_TERMS, user)
    latest = TermsAndConditions.get_latest(PAYMENT_TERMS)
    ok = False
    if accepted and latest:
        ok = accepted.terms.version == latest.version
    payment_terms = {'accepted': accepted,
                      'latest': latest,
                      'ok': ok}
    return payment_terms


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

    course_modes = defaultdict(list)
    modes = CourseMode.objects.all()
    for course in modes:
        course_modes[unicode(course.course_id)].append([course.mode_slug, course.min_price])

    for enrollment in CourseEnrollment.objects.filter(user=user):
        key = unicode(enrollment.course_id)
        optout = key in optouts
        course = get_course(key)
        if not course:
            continue  # enrollment can exists for course that does not exist anymore in mongo
        title = course.display_name
        course_roles = user_roles.get(key, [])
        enrollments.append((title, unicode(enrollment.course_id), optout, enrollment.mode,
                course_roles, enrollment.is_active))

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
        'certificates': certificates,
        'course_modes': course_modes,
        'payment_terms': get_accepted_payment_terms(user),
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
