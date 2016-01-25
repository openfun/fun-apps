# -*- coding: utf-8 -*-

import datetime
from dateutil.parser import parse as dateutil_parse

from celery import shared_task

from django.core.management import call_command


@shared_task
def update_courses_meta_data(*args, **kwargs):
    '''
    A task that servers as proxy to the management command.
    Can be used for instance when a signal is fired to update
    a single course or to run periodic tasks.
    '''

    now = datetime.datetime.now().isoformat()
    call_command('update_courses', *args, **kwargs)
    call_command('update_index', start_date=now, *args, **kwargs)
