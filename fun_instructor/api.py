from celery.states import READY_STATES

from instructor_task.api_helper import submit_task
from instructor_task.models import InstructorTask

from tasks import task_generate_certificate

def submit_generate_certificate(request, course_key, query_features):
    """ Request to generate certificate as a background task. """
    task_type = 'certificate-generation'
    task_class = task_generate_certificate
    task_input = query_features
    task_key = ""

    return submit_task(request, task_type, task_class, course_key, task_input, task_key)


def get_running_instructor_tasks(course_id, task_type):
    """
    Returns a query of InstructorTask objects of running tasks for a given course and task type
    """
    instructor_tasks = InstructorTask.objects.filter(course_id=course_id, task_type=task_type)
    # exclude states that are "ready" (i.e. not "running", e.g. failure, success, revoked):
    for state in READY_STATES:
        instructor_tasks = instructor_tasks.exclude(task_state=state)
    return instructor_tasks.order_by('-id')

