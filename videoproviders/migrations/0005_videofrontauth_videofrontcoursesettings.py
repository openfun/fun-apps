# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
        ('videoproviders', '0004_del_libcast'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideofrontAuth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('token', models.CharField(max_length=128, verbose_name='Access token')),
                ('university', models.OneToOneField(null=True, blank=True, to='universities.University', verbose_name='Associated university')),
            ],
        ),
        migrations.CreateModel(
            name='VideofrontCourseSettings',
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
