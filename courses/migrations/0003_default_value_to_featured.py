# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coursesubject',
            name='featured',
            field=models.BooleanField(default=False, db_index=True, verbose_name='featured'),
        ),
    ]
