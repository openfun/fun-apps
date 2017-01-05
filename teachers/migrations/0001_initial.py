# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20161011_1739'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTeacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name='order')),
                ('course', models.ForeignKey(related_name='certificateteacher_related', to='courses.Course')),
            ],
            options={
                'ordering': ('order', 'id'),
                'abstract': False,
                'verbose_name': 'certificate teacher',
                'verbose_name_plural': 'certificate teachers',
            },
        ),
        migrations.CreateModel(
            name='CourseTeacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.PositiveIntegerField(default=0, verbose_name='order')),
                ('course', models.ForeignKey(related_name='courseteacher_related', to='courses.Course')),
            ],
            options={
                'ordering': ('order', 'id'),
                'abstract': False,
                'verbose_name': 'course teacher',
                'verbose_name_plural': 'course teachers',
            },
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('full_name', models.CharField(max_length=300, verbose_name='Full name')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='slug')),
                ('profile_image', models.ImageField(upload_to=b'teachers', null=True, verbose_name='profile image', blank=True)),
                ('bio', ckeditor.fields.RichTextField(verbose_name='bio', blank=True)),
            ],
            options={
                'verbose_name': 'teacher',
                'verbose_name_plural': 'teachers',
            },
        ),
        migrations.AddField(
            model_name='courseteacher',
            name='teacher',
            field=models.ForeignKey(related_name='+', to='teachers.Teacher'),
        ),
        migrations.AddField(
            model_name='certificateteacher',
            name='teacher',
            field=models.ForeignKey(related_name='+', to='teachers.Teacher'),
        ),
        migrations.AlterUniqueTogether(
            name='courseteacher',
            unique_together=set([('course', 'teacher')]),
        ),
        migrations.AlterUniqueTogether(
            name='certificateteacher',
            unique_together=set([('course', 'teacher')]),
        ),
    ]
