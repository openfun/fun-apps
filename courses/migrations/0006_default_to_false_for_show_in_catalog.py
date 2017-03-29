# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_add_show_about_page_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='show_in_catalog',
            field=models.BooleanField(default=False, help_text='Controls whether a course is listed in the courses catalog page', db_index=True, verbose_name='show in catalog'),
        ),
    ]
