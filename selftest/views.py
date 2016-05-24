# -*- coding: utf-8 -*-

import os
import platform

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.utils.translation import get_language
from django.views.debug import get_safe_settings

from dealer.git import git

from .forms import EmailForm
from selftest.tasks import trigger_worker_error


repositories = [
        'edx-platform', 'fun-config', 'fun-apps',
        '../forum/cs_comments_service',
        'venvs/edxapp/src/edx-ora2',
        'venvs/edxapp/src/proctoru-xblock',
        'venvs/edxapp/src/libcast-xblock',
        'venvs/edxapp/src/edx-gea',
        ]


@user_passes_test(lambda u: u.is_superuser)
def selftest_index(request):
    if not request.user.is_superuser:
        raise Http404

    emailform = EmailForm(request.POST or None)

    if request.method == 'POST':
        if emailform.is_valid():
            subj = "Test email from FUN server %s %s" % (settings.SERVICE_VARIANT, settings.SITE_NAME)
            msg = emailform.cleaned_data['text']
            to = emailform.cleaned_data['to']
            send_mail(subj, msg, settings.SERVER_EMAIL, [to])
            messages.add_message(request, messages.INFO, 'Mail sent to %s.' % to)
            return HttpResponseRedirect(reverse('self-test-index'))

    misc = {}
    misc['get_language'] = get_language()
    misc['platform_node'] = platform.node()

    revisions = {}
    for repo in repositories:
        try:
            os.chdir(settings.BASE_ROOT / repo)
            git.path = settings.BASE_ROOT / repo
            git.init_repo()
            revisions[repo] = mark_safe(git.repo.git(
                'log -1 --decorate --format=<strong>%h</strong>&nbsp;%aD&nbsp;%d<br><strong>%s</strong>&nbsp;%ae'
            ))
        except Exception as e:
            revisions[repo] = mark_safe("<strong>Unknown</strong> %r" % e)


    return render(request, 'selftest/index.html', {
        'emailform': emailform,
        'misc': misc,
        'settings': get_safe_settings(),
        'environ': os.environ,
        'revisions': revisions,
    })


@user_passes_test(lambda u: u.is_superuser)
def page_not_found(request):
    if not request.user.is_superuser:
        raise Http404
    raise Http404("This is an intentional 404 (page not found).")


@user_passes_test(lambda u: u.is_superuser)
def server_error(request):
    if not request.user.is_superuser:
        raise Http404
    raise Exception("This is an intentional 500 (server error).")


@user_passes_test(lambda u: u.is_superuser)
def worker_error(request):
    task = trigger_worker_error.apply_async()
    messages.add_message(request, messages.INFO, "Request sent. Task id: {}".format(task.id))
    return HttpResponseRedirect(reverse('self-test-index'))


