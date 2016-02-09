from django.dispatch import receiver

from xmodule.modulestore.django import SignalHandler


@receiver(SignalHandler.course_published, dispatch_uid='fun.courses.signals.update_courses')
def update_course_meta_data_on_studio_publish(sender, course_key, **kwargs):
    from django.conf import settings
    if getattr(settings, "COURSE_SIGNALS_DISABLED", False):
        return 'FUN courses meta data update has been skipped.'

    from .tasks import update_courses_meta_data
    # course_key is a CourseKey object and course_id its sting representation
    update_courses_meta_data.delay(course_id=unicode(course_key))
    return 'FUN courses meta data update has been triggered.'
