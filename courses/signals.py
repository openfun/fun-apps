from django.dispatch import receiver

from student.signals import ENROLL_STATUS_CHANGE
from student.models import EnrollStatusChange
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
    ENROLL_STATUS_CHANGE,
    dispatch_uid='fun.courses.signals.change_enrollment_status')
def sync_openedx_to_richie_after_enrollment_status_change(
        sender, event=None, course_id=None, **kwargs
    ):
    """
    Trigger hook when changing a course enrollment and the change if of the type "enroll
    """

    if event != EnrollStatusChange.enroll:
        return (
            'FUN courses meta data update has been skipped, '
            'because the event status change is not about enroll'
        )

    from .tasks import update_courses_meta_data
    # course_key is a CourseKey object and course_id its string representation
    update_courses_meta_data.delay(course_id=unicode(course_id))
    return 'FUN courses meta data update has been triggered from enrollment status change.'
