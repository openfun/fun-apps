# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LibcastAuth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(max_length=255, verbose_name='Username (not the email address)')),
                ('api_key', models.CharField(max_length=255, verbose_name='API key')),
                ('university', models.OneToOneField(verbose_name='Associated university', to='universities.University')),
            ],
        ),
        migrations.CreateModel(
            name='LibcastCourseSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.CharField(unique=True, max_length=200, verbose_name='Course ID')),
                ('directory_slug', models.CharField(max_length=200, verbose_name='Libcast directory slug')),
                ('stream_slug', models.CharField(max_length=200, verbose_name='Libcast stream slug')),
            ],
            options={
                'verbose_name_plural': 'Libcast course settings',
            },
        ),
    ]
