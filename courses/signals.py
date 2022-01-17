from django.db.models.signals import post_save
from django.dispatch import receiver

from student.models import CourseEnrollment
from xmodule.modulestore.django import SignalHandler


@receiver(SignalHandler.course_published, dispatch_uid='fun.courses.signals.update_courses')
def update_course_meta_data_on_studio_publish(sender, course_key, **kwargs):
    """Trigger hook when publishing a change to a course"""
    from django.conf import settings
    if getattr(settings, "COURSE_SIGNALS_DISABLED", False):
        return 'FUN courses meta data update has been skipped.'

    from .tasks import update_courses_meta_data
    # course_key is a CourseKey object and course_id its string representation
    update_courses_meta_data.delay(course_id=unicode(course_key))
    return 'FUN courses meta data update has been triggered from course publish.'


@receiver(
    post_save,
    sender=CourseEnrollment,
    dispatch_uid='fun.courses.signals.sync_to_richie')
def sync_openedx_to_richie_post_enrollment_save(sender, instance, **kwargs):
    """Trigger hook when changing a course enrollment."""
    from .tasks import update_courses_meta_data
    # course_key is a CourseKey object and course_id its string representation
    update_courses_meta_data.delay(course_id=unicode(instance.course_id))
    return 'FUN courses meta data update has been triggered from enrollment status change.'
