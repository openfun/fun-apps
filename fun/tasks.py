# -*- coding: utf-8 -*-

from celery import shared_task

from django.core.management import call_command


@shared_task
def update_search_index(*args, **kwargs):
    '''
    A task that serves as proxy to the management command
    for updating search index.
    Can be used for instance to run periodic tasks.
    '''
    call_command('update_index', *args, **kwargs)
