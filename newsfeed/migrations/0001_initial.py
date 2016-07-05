# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import re
import django.utils.timezone
import django.core.validators
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=256, verbose_name='title')),
                ('slug', models.SlugField(unique=True, verbose_name='slug', validators=[django.core.validators.RegexValidator(re.compile('^[-a-zA-Z0-9_]+\\Z'), "Enter a valid 'slug' consisting of letters, numbers, underscores or hyphens.", 'invalid')])),
                ('thumbnail', models.ImageField(help_text='Displayed on the news list page.', upload_to=b'newsfeed', null=True, verbose_name='thumbnail', blank=True)),
                ('lead_paragraph', models.CharField(max_length=256, verbose_name='Lead paragraph', blank=True)),
                ('text', ckeditor.fields.RichTextField(verbose_name='text', blank=True)),
                ('event_date', models.DateTimeField(null=True, verbose_name='event date', blank=True)),
                ('language', models.CharField(default=b'fr', max_length=8, verbose_name='language', choices=[(b'fr', b'Fran\xc3\xa7ais'), (b'en', b'English'), (b'de-de', b'Deutsch')])),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at', db_index=True)),
                ('edited_at', models.DateTimeField(auto_now=True, verbose_name='edited at')),
                ('published', models.BooleanField(default=False, verbose_name='published')),
                ('microsite', models.CharField(db_index=True, max_length=128, blank=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ArticleCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('slug', models.SlugField(unique=True, max_length=255, verbose_name='slug')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='order')),
            ],
            options={
                'ordering': ('order', 'id'),
                'verbose_name': 'Article Category',
                'verbose_name_plural': 'Article Categories',
            },
        ),
        migrations.CreateModel(
            name='ArticleLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name')),
                ('url', models.CharField(max_length=255, verbose_name='url')),
                ('article', models.ForeignKey(related_name='links', verbose_name='article', to='newsfeed.Article')),
            ],
            options={
                'verbose_name': 'Article Link',
                'verbose_name_plural': 'Article Links',
            },
        ),
        migrations.AddField(
            model_name='article',
            name='category',
            field=models.ForeignKey(related_name='articles', verbose_name='category', blank=True, to='newsfeed.ArticleCategory', null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='courses',
            field=models.ManyToManyField(related_name='articles', verbose_name='courses', to='courses.Course'),
        ),
    ]
