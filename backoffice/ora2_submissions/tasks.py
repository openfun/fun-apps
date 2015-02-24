from celery import task
import celery.states
import json
import os

from instructor_task.api_helper import submit_task
from instructor_task.models import InstructorTask
from instructor_task.tasks_helper import (
    BaseInstructorTask,
    run_main_task
)

from fun.management.commands.generate_oa_data import Command as OaCommand
import fun.shared


PREPARATION_TASK_TYPE = "ora2-submissions-preparation",


def submit_preparation_task(request, course_key):
    # Make sure that the same task cannot run twice for the same course
    task_key = course_key.to_deprecated_string()
    task_input = None
    return submit_task(
        request,
        PREPARATION_TASK_TYPE,
        prepare_ora2_submissions_task,
        course_key,
        task_input,
        task_key
    )

@task(base=BaseInstructorTask)
def prepare_ora2_submissions_task(entry_id, _xmodule_instance_args):
    action_name = "generated"
    return run_main_task(entry_id, prepare_ora2_submissions_main_task, action_name)

def prepare_ora2_submissions_main_task(_entry_id, course_key, _task_input, _action_name):
    delete_previous_files(course_key)
    output_file_name = prepare_ora2_submissions_file(course_key.to_deprecated_string())
    return {
        "path": output_file_name,
    }

def delete_previous_files(course_id):
    for instructor_task in get_last_instructor_tasks(course_id):
        file_path = get_output_path(instructor_task)
        if os.path.exists(file_path):
            os.remove(file_path)
        instructor_task.task_output = None
        instructor_task.save()

def prepare_ora2_submissions_file(course_key_string):
    output_file = fun.shared.NamedTemporaryFile(dir="ora2-submissions", suffix=".tar.gz", delete=False)
    OaCommand().dump_to(course_key_string, output_file.name)
    return output_file.name

def file_is_prepared(course_id):
    instructor_task = get_last_instructor_task(course_id)
    return instructor_task is not None

def get_file_path(course_id):
    instructor_task = get_last_instructor_task(course_id)
    if instructor_task is None:
        return None
    return get_output_path(instructor_task)

def get_output_path(instructor_task):
    task_output = json.loads(instructor_task.task_output)
    return task_output["path"]

def get_last_instructor_task(course_id):
    objects = get_last_instructor_tasks(course_id)[:1]
    return objects[0] if objects else None

def get_last_file_date(course_id):
    instructor_task = get_last_instructor_task(course_id)
    return instructor_task.updated if instructor_task else None

def get_last_instructor_tasks(course_id):
    return InstructorTask.objects.filter(
        course_id=course_id,
        task_type=PREPARATION_TASK_TYPE,
        task_output__isnull=False
    ).order_by("-pk")

def is_task_running(course_id):
    return InstructorTask.objects.filter(
        course_id=course_id,
        task_type=PREPARATION_TASK_TYPE,
        task_state__in=celery.states.UNREADY_STATES
    ).count() > 0
