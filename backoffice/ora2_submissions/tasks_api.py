from instructor_task.api_helper import submit_task

from fun_instructor.tasks import prepare_ora2_submissions_task
from . import tasks


def submit_preparation_task(request, course_key):
    return submit_task(
        request,
        tasks.PREPARATION_TASK_TYPE,
        prepare_ora2_submissions_task,
        course_key,
        None,
        get_task_key(course_key)
    )

def get_task_key(course_id):
    # Make sure that the same task cannot run twice for the same course
    return "ora2-submissions-preparation-" + course_id.to_deprecated_string()

def file_is_prepared(course_id):
    return get_last_successful_instructor_task(course_id) is not None

def get_file_path(course_id):
    instructor_task = get_last_successful_instructor_task(course_id)
    if instructor_task is None:
        return None
    return tasks.get_output_path(instructor_task)

def get_last_file_date(course_id):
    instructor_task = get_last_successful_instructor_task(course_id)
    return instructor_task.updated if instructor_task else None

def get_last_successful_instructor_task(course_id):
    objects = tasks.get_last_successful_instructor_tasks(course_id)[:1]
    return objects[0] if objects else None

def is_task_running(course_id):
    return tasks.get_last_unready_instructor_tasks(course_id).count() > 0
