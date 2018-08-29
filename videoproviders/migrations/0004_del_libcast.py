# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videoproviders', '0002_videouploaderdeactivationperiod_youtubeauth_youtubecoursesettings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libcastauth',
            name='university',
        ),
        migrations.DeleteModel(
            name='LibcastCourseSettings',
        ),
        migrations.DeleteModel(
            name='LibcastAuth',
        ),
    ]
