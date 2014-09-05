# -*- coding: utf-8 -*-

import os
import platform

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import get_language
from django.views.debug import get_safe_settings

from dealer.git import git

from .forms import EmailForm


repositories = ['edx-platform', 'fun-config', 'fun-apps', 'themes/fun']


#@user_passes_test(lambda u: u.is_superuser)
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
        os.chdir(settings.BASE_ROOT / repo)
        git.path = settings.BASE_ROOT / repo
        git.init_repo()
        revisions[repo] = git.revision

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