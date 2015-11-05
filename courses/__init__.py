# Django signal receiver modules must imported early so that the signal
# handling gets registered before any signals need to be sent.

from .signals import update_course_meta_data_on_studio_publish
