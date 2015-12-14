from celery import task

@task
def trigger_worker_error():
    raise Exception("This is an intentional 500 triggered in a celery task.")
