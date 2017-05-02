from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from xmodule_django.models import CourseKeyField



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


class VideofrontAuth(models.Model):
    university = models.OneToOneField("universities.University",
                                      blank=True, null=True,
                                      verbose_name=_("Associated university"))
    token = models.CharField(verbose_name=_("Access token"), max_length=128)

    def __unicode__(self):
        return u"VideofrontAuth: %s" % self.university.name


class VideofrontCourseSettings(models.Model):
    """
    Store the Videofront settings for each course. Normally, these fields should
    be completed automatically by the videofront videoproviders app. Note that in
    the case of a second course session, you might want to assign to the
    corresponding course setting the same values as the course setting for the
    first run.
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    playlist_id = models.CharField(verbose_name=_("Playlist ID"), max_length=128)

    class Meta:
        ordering = ('course_id',)

    def __unicode__(self):
        return u"VideofrontCourseSettings: course: %s playlist: %s" % (
                self.course_id, self.playlist_id)


class BokeCCCourseSettings(models.Model):
    """
    Store the BokeCC settings for each course. Normally, these fields should
    be completed automatically by the BokeCC app. Note that in
    the case of a second course session, you might want to assign to the
    corresponding course setting the same values as the course setting for the
    first run.
    """
    course_id = CourseKeyField(max_length=255, db_index=True)
    playlist_id = models.CharField(verbose_name=_("Playlist ID"), max_length=128)

    class Meta:
        ordering = ('course_id',)
