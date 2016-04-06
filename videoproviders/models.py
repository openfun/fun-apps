from django.db import models
from django.utils.translation import ugettext_lazy as _


class AuthManager(models.Manager):

    def get_for_course(self, course):
        return self.get(university__code=course.location.org)


class LibcastAuth(models.Model):
    university = models.OneToOneField("universities.University", verbose_name=_("Associated university"))

    username = models.CharField(verbose_name=_("Username (not the email address)"), max_length=255)
    api_key = models.CharField(verbose_name=_("API key"), max_length=255)

    objects = AuthManager()


class LibcastCourseSettings(models.Model):
    """
    Store the libcast settings for each course. This object will be created
    if necessary but can be modified by the support team.
    """
    course = models.CharField(verbose_name=_("Course ID"), max_length=200, unique=True)

    # Directory in which the course files are stored
    directory_slug = models.CharField(verbose_name=_("Libcast directory slug"), max_length=200)

    # Stream in which the course resources are stored
    stream_slug = models.CharField(verbose_name=_("Libcast stream slug"), max_length=200)

    class Meta:
        verbose_name_plural = _("Libcast course settings")
