from instructor_task.api_helper import submit_task

from tasks import task_generate_certificate

def submit_generate_certificate(request, course_key, query_features):
    """ Request to generate certificate as a background task. """
    task_type = 'certificate-generation'
    task_class = task_generate_certificate
    task_input = query_features
    task_key = ""

    return submit_task(request, task_type, task_class, course_key, task_input, task_key)
