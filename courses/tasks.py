from celery import shared_task

from django.core.management import call_command


@shared_task
def update_courses_meta_data(*args, **kwargs):
    '''
    A task that servers as proxy to the management command.
    Can be used for instance when a signal is fired to update
    a single course or to run periodic tasks.
    '''
    call_command('update_courses', *args, **kwargs)
