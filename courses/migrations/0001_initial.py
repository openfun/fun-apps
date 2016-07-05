# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('modification_date', models.DateTimeField(auto_now=True, verbose_name='modification date')),
                ('key', models.CharField(unique=True, max_length=200, verbose_name='Course key')),
                ('title', models.CharField(max_length=255, verbose_name='title', blank=True)),
                ('university_display_name', models.CharField(help_text='Displayed in place of the university name. If not set, use the name of the first associated university.', max_length=255, verbose_name='university display name', blank=True)),
                ('short_description', models.TextField(verbose_name='short description', blank=True)),
                ('image_url', models.CharField(max_length=255, verbose_name='image url', blank=True)),
                ('level', models.CharField(blank=True, max_length=255, verbose_name='level', db_index=True, choices=[(b'introductory', 'Introductory'), (b'intermediate', 'Intermediate'), (b'advanced', 'Advanced')])),
                ('language', models.CharField(default=b'fr', max_length=255, verbose_name='language', db_index=True, choices=[(b'de', 'German'), (b'en', 'English'), (b'fr', 'French')])),
                ('show_in_catalog', models.BooleanField(default=True, help_text='Controls whether a course is listed in the courses catalog page', db_index=True, verbose_name='show in catalog')),
                ('is_active', models.BooleanField(default=False, verbose_name='is active')),
                ('prevent_auto_update', models.BooleanField(default=False, help_text='prevent score automatic update', verbose_name='No auto update')),
                ('session_number', models.PositiveIntegerField(default=1, help_text="Set 0 if session doesn't make sense for this course.", verbose_name='session')),
                ('score', models.PositiveIntegerField(default=0, verbose_name='score', db_index=True)),
                ('start_date', models.DateTimeField(db_index=True, null=True, verbose_name='start date', blank=True)),
                ('end_date', models.DateTimeField(db_index=True, null=True, verbose_name='end date', blank=True)),
                ('enrollment_start_date', models.DateTimeField(db_index=True, null=True, verbose_name='enrollment start date', blank=True)),
                ('enrollment_end_date', models.DateTimeField(db_index=True, null=True, verbose_name='enrollment end date', blank=True)),
                ('thumbnails_info', jsonfield.fields.JSONField(null=True, verbose_name='thumbnails info', blank=True)),
                ('certificate_passing_grade', models.FloatField(help_text='Percentage, between 0 and 1', null=True, verbose_name='verified certificate passing grade', blank=True)),
            ],
            options={
                'ordering': ('-score',),
                'verbose_name': 'course',
                'verbose_name_plural': 'courses',
            },
        ),
        migrations.CreateModel(
            name='CourseSubject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name', db_index=True)),
                ('short_name', models.CharField(help_text='Displayed where space is rare - on side panel for instance.', max_length=255, verbose_name='short name', blank=True)),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='slug')),
                ('description', ckeditor.fields.RichTextField(verbose_name='description', blank=True)),
                ('featured', models.BooleanField(db_index=True, verbose_name='featured')),
                ('image', models.ImageField(upload_to=b'courses', null=True, verbose_name='image', blank=True)),
                ('score', models.PositiveIntegerField(default=0, verbose_name='score', db_index=True)),
            ],
            options={
                'ordering': ('-score', 'name', 'id'),
                'verbose_name': 'Course Subject',
                'verbose_name_plural': 'Course Subjects',
            },
        ),
        migrations.CreateModel(
            name='CourseUniversityRelation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name='order', db_index=True)),
                ('course', models.ForeignKey(related_name='related_universities', to='courses.Course')),
                ('university', models.ForeignKey(related_name='related_courses', to='universities.University')),
            ],
            options={
                'ordering': ('order', 'id'),
                'verbose_name': 'course-university relation',
                'verbose_name_plural': 'course-university relation',
            },
        ),
        migrations.AddField(
            model_name='course',
            name='subjects',
            field=models.ManyToManyField(related_name='courses', to='courses.CourseSubject'),
        ),
        migrations.AddField(
            model_name='course',
            name='universities',
            field=models.ManyToManyField(related_name='courses', through='courses.CourseUniversityRelation', to='universities.University'),
        ),
        migrations.AlterUniqueTogether(
            name='courseuniversityrelation',
            unique_together=set([('university', 'course')]),
        ),
    ]
