# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import xmodule_django.models


class Migration(migrations.Migration):

    dependencies = [
        ('videoproviders', '0006_explicitely_set_is_youtube_video_xblock_attribute'),
    ]

    operations = [
        migrations.CreateModel(
            name='BokeCCCourseSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', xmodule_django.models.CourseKeyField(max_length=255, db_index=True)),
                ('playlist_id', models.CharField(max_length=128, verbose_name='Playlist ID')),
            ],
            options={
                'ordering': ('course_id',),
            },
        ),
    ]
