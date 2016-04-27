# -*- coding: utf-8 -*-

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class TermsAndConditions(models.Model):
    name = models.CharField(max_length=100, verbose_name=_(u"Name"))
    version = models.CharField(max_length=12, verbose_name=_(u"Terms and conditions version (semver)"))
    datetime = models.DateTimeField(auto_now_add=True, verbose_name=_(u"Acceptance date"))
    text = models.TextField(verbose_name=_(u"Terms and conditions content (HTML allowed)"))

    def __unicode__(self):
        return u"%s v%s" % (self.name, self.version)

    class Meta:
        verbose_name = _(u"Terms and conditions")
        verbose_name_plural = _(u"Terms and conditions")
        ordering = ['name', '-datetime']

    @classmethod
    def version_accepted(cls, name, user):
        try:
            return UserAcceptance.objects.get(terms__name=name, user=user)
        except UserAcceptance.DoesNotExist:
            return None

    @classmethod
    def get_latest(cls, name):
        try:
            return TermsAndConditions.objects.filter(name=name).latest('datetime')
        except TermsAndConditions.DoesNotExist:
            return None

    @classmethod
    def user_has_to_accept_new_version(cls, name, user):
        latest = TermsAndConditions.get_latest(name=name)
        if latest is None:
            return False  # terms do not exists yet, user is ok
        if latest.version == '0':  # terms of version 0 are considered as accepted
            return False
        accepted = TermsAndConditions.version_accepted(name, user)
        if accepted and accepted.terms.version == latest.version:
            return False   # user already has accepted latest version
        else:
            return latest # user has to accept latest version

    def accept(self, user):
        accepted, created = UserAcceptance.objects.get_or_create(terms=self, user=user)
        if not created:
            if accepted.terms == self:
                return False  # user has already accepted those terms
            accepted.terms = self  # update accepted version
            accepted.save()
        return True


class UserAcceptance(models.Model):
    user = models.ForeignKey(User, related_name='terms_accepted')
    terms = models.ForeignKey(TermsAndConditions, related_name='accepted')
    datetime = models.DateTimeField(auto_now=True, verbose_name=_(u"Acceptance date"))

    def __unicode__(self):
        return u"%s: %s v%s" % (self.user.username, self.terms.name, self.terms.version)

    class Meta:
        verbose_name = _(u"User terms and conditions acceptance")
        unique_together = ['user', 'terms']

