from datetime import timedelta
from time import time

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now


class DailymotionAuthManager(models.Manager):

    def get_for_course(self, course):
        return self.get(university__code=course.location.org)


class DailymotionAuth(models.Model):
    university = models.OneToOneField("universities.University", verbose_name=_("Associated university"))

    username = models.CharField(verbose_name=_("Username (email address)"), max_length=255)
    password = models.CharField(verbose_name=_("Password"), max_length=255)

    api_key = models.CharField(verbose_name=_("API key"), max_length=255)
    api_secret = models.CharField(verbose_name=_("API secret"), max_length=255)

    access_token = models.CharField(verbose_name=_("Access token"), max_length=255)
    refresh_token = models.CharField(verbose_name=_("Refresh token"), max_length=255)
    expires_at = models.IntegerField(verbose_name=_("Token expiry time"), default=0)

    objects = DailymotionAuthManager()

    def update_token(self, access_token, refresh_token, expires_at):
        if self.access_token != access_token or self.refresh_token != refresh_token or self.expires_at != expires_at:
            self.access_token = access_token
            self.refresh_token = refresh_token
            self.expires_at = expires_at
            self.save()

    @property
    def expires_at_time(self):
        return now() + timedelta(seconds=(self.expires_at - time()))
