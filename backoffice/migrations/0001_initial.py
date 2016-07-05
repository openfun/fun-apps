# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djcelery', '__first__'),
        ('student', '0005_auto_20160531_1653'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoginFailuresProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Temporary account suspension',
                'proxy': True,
                'verbose_name_plural': 'Temporary account suspensions',
            },
            bases=('student.loginfailures',),
        ),
        migrations.CreateModel(
            name='TaskMetaProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Celery task result',
                'proxy': True,
                'verbose_name_plural': 'Celery task results',
            },
            bases=('djcelery.taskmeta',),
        ),
        migrations.CreateModel(
            name='TaskSetMetaProxy',
            fields=[
            ],
            options={
                'verbose_name': 'Celery taskset result',
                'proxy': True,
                'verbose_name_plural': 'Celery taskset results',
            },
            bases=('djcelery.tasksetmeta',),
        ),
    ]
