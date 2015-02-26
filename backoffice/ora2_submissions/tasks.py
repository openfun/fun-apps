import celery.states
import json
import os

from instructor_task.models import InstructorTask

from fun.management.commands.generate_oa_data import Command as OaCommand
import fun.shared


PREPARATION_TASK_TYPE = "ora2-submissions-preparation",


def prepare_ora2_submissions(_entry_id, course_key, _task_input, _action_name):
    delete_previous_files(course_key)
    output_file_name = prepare_ora2_submissions_file(course_key.to_deprecated_string())
    return {
        "path": output_file_name,
    }

def delete_previous_files(course_id):
    for instructor_task in get_last_successful_instructor_tasks(course_id):
        file_path = get_output_path(instructor_task)
        if os.path.exists(file_path):
            os.remove(file_path)
        instructor_task.task_output = None
        instructor_task.save()

def prepare_ora2_submissions_file(course_key_string):
    output_file = fun.shared.NamedTemporaryFile(dir="ora2-submissions", suffix=".tar.gz", delete=False)
    OaCommand().dump_to(course_key_string, output_file.name)
    return output_file.name

def get_output_path(instructor_task):
    task_output = json.loads(instructor_task.task_output)
    return task_output["path"]

def get_last_unready_instructor_tasks(course_id):
    return get_last_instructor_tasks(course_id).exclude(
        task_state__in=celery.states.READY_STATES
    )

def get_last_successful_instructor_tasks(course_id):
    return get_last_instructor_tasks(course_id).filter(
        task_state=celery.states.SUCCESS
    )

def get_last_instructor_tasks(course_id):
    return InstructorTask.objects.filter(
        course_id=course_id,
        task_type=PREPARATION_TASK_TYPE,
    ).order_by("-pk")
