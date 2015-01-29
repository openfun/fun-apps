# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _


from universities.models import University


class Course(models.Model):
    key = models.CharField(max_length=200, verbose_name=_(u"Course key"))
    university = models.ForeignKey(University, null=True, related_name='courses')

    class Meta:
        verbose_name = "Fun course"

    def __unicode__(self):
        return u"FUN course: %s" % self.key


class Teacher(models.Model):
    course = models.ForeignKey(Course)
    title = models.CharField(max_length=100, verbose_name=_("Titre"))
    full_name = models.CharField(max_length=300, verbose_name=_("Nom complet"))
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "FUN teacher"

    def __unicode__(self):
        return u"FUN teacher: %s %s" % (self.title, self.full_name)
