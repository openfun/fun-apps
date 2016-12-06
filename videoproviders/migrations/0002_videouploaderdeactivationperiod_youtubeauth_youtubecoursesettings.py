# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone

from openedx.core.djangoapps.xmodule_django.models import CourseKeyField

class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
        ('videoproviders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoUploaderDeactivationPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(verbose_name='Start time', db_index=True)),
                ('end_time', models.DateTimeField(verbose_name='End time', db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='YoutubeAuth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('client_id', models.CharField(unique=True, max_length=128, verbose_name='Client ID')),
                ('client_secret', models.CharField(max_length=128, verbose_name='Client secret')),
                ('access_token', models.CharField(max_length=128, verbose_name='Access token')),
                ('refresh_token', models.CharField(max_length=128, verbose_name='Refresh token')),
                ('token_expiry', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Token expiry', blank=True)),
                ('university', models.OneToOneField(null=True, blank=True, to='universities.University', verbose_name='Associated university')),
            ],
        ),
        migrations.CreateModel(
            name='YoutubeCourseSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_id', CourseKeyField(max_length=255, db_index=True)),
                ('playlist_id', models.CharField(max_length=128, verbose_name='Playlist ID')),
            ],
            options={
                'ordering': ('course_id',),
            },
        ),
    ]
