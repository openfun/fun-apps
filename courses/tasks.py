from celery import shared_task
from celery.decorators import periodic_task
from celery.task.schedules import crontab

from django.core.management import call_command

from . import settings as courses_settings


@shared_task
def update_courses_meta_data(*args, **kwargs):
    '''
     A task that servers as proxy to the management command.
     Can be used for  instance when a signal is fired to update
     a single course.
    '''
    call_command('update_courses', *args, **kwargs)


@periodic_task(run_every=(crontab(**courses_settings.COURSES_META_DATA_UPDATE_CRONTAB)))
def update_course_meta_data_periodically():
    '''
    A periodic task that update all courses.
    '''
    call_command('update_courses')
