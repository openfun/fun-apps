# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import ckeditor.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, verbose_name='name', db_index=True)),
                ('short_name', models.CharField(help_text='Displayed where space is rare - on side panel for instance.', max_length=255, verbose_name='short name', blank=True)),
                ('code', models.CharField(unique=True, max_length=255, verbose_name='code')),
                ('certificate_logo', models.ImageField(help_text='Logo to be displayed on the certificate document.', upload_to=b'universities', null=True, verbose_name='certificate logo', blank=True)),
                ('logo', models.ImageField(upload_to=b'universities', verbose_name='logo')),
                ('detail_page_enabled', models.BooleanField(default=False, help_text='Enables the university detail page.', db_index=True, verbose_name='detail page enabled')),
                ('is_obsolete', models.BooleanField(default=False, help_text='Obsolete universities do not have their logo displayed on the site.', db_index=True, verbose_name='is obsolete')),
                ('slug', models.SlugField(max_length=255, blank=True, help_text='Only used if detail page is enabled', unique=True, verbose_name='slug')),
                ('banner', models.ImageField(upload_to=b'universities', null=True, verbose_name='banner', blank=True)),
                ('description', ckeditor.fields.RichTextField(verbose_name='description', blank=True)),
                ('partnership_level', models.CharField(blank=True, max_length=255, verbose_name='partnership level', db_index=True, choices=[(b'simple-partner', 'Partner'), (b'academic-partner', 'Academic Partner'), (b'level-1', 'Level 1'), (b'level-2', 'Level 2'), (b'level-3', 'Level 3')])),
                ('score', models.PositiveIntegerField(default=0, verbose_name='score', db_index=True)),
                ('prevent_auto_update', models.BooleanField(default=False, verbose_name='prevent automatic update')),
            ],
            options={
                'ordering': ('-score', 'id'),
                'verbose_name': 'University',
                'verbose_name_plural': 'Universit\xe9s',
            },
        ),
    ]
