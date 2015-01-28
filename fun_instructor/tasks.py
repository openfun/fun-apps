from celery import task
from functools import partial

from django.utils.translation import ugettext_noop
from tasks_helper import generate_certificate
from instructor_task.tasks_helper import (
    BaseInstructorTask,
    run_main_task
)

@task(base=BaseInstructorTask)
def task_generate_certificate(entry_id, xmodule_instance_args):
    """ """

    action_name = ugettext_noop('certified')
    task_fn = partial(generate_certificate, xmodule_instance_args)
    return run_main_task(entry_id, task_fn, action_name)


