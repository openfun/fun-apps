from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from xmodule_django.models import CourseKeyField


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


class VideoUploaderDeactivationPeriod(models.Model):
    """
    Define periods of time during which the CMS videoupload dashboard cannot be
    accessed.
    """
    start_time = models.DateTimeField(verbose_name=_("Start time"), db_index=True)
    end_time = models.DateTimeField(verbose_name=_("End time"), db_index=True)


class YoutubeAuth(models.Model):
    """
    Youtube API credentials for the whole platform. There is one account per
    university, in order to avoid having our single account blocked on account
    of copyriht reasons.

    This is how you can obtain credentials for a university:
    1) Head to https://console.developers.google.com/
    2) Activate the "Youtube Data API" (you need to create a project for that)
    3) Create an "OAuth Client ID" for an "Other" type of application
    4) Download the client_secret_*.json file that was generated
    5) Run the "youtube-auth" management command to store the access tokens
    """
    university = models.OneToOneField("universities.University",
                                      blank=True, null=True,
                                      verbose_name=_("Associated university"))

    client_id = models.CharField(verbose_name=_("Client ID"), max_length=128, unique=True)
    client_secret = models.CharField(verbose_name=_("Client secret"), max_length=128)
    access_token = models.CharField(verbose_name=_("Access token"), max_length=128)
    refresh_token = models.CharField(verbose_name=_("Refresh token"), max_length=128)
    token_expiry = models.DateTimeField(verbose_name=_("Token expiry"), default=now, blank=True, null=True)


class YoutubeCourseSettings(models.Model):
    """
    Store the Youtube settings for each course. Normally, these fields should
    be completed automatically by the youtube videoproviders app. Note that in
    the case of a second course session, you might want to assign to the
    corresponding course setting the same values as the course setting for the
    first run.
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    playlist_id = models.CharField(verbose_name=_("Playlist ID"), max_length=128)

    class Meta:
        ordering = ('course_id',)
