# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0006_default_to_false_for_show_in_catalog'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='key',
            field=models.CharField(unique=True, max_length=255, verbose_name='Course key'),
        ),
    ]
