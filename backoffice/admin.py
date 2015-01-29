# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Course, Teacher


admin.site.register(Course)
admin.site.register(Teacher)
