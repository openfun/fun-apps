# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_auto_20161011_1739'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='show_about_page',
            field=models.BooleanField(default=True, help_text='Controls whether the course about page is visible', db_index=True, verbose_name='show course about page'),
        ),
    ]
