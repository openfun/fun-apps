# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0007_auto_20190403_1113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='active'),
        ),
        migrations.AlterField(
            model_name='course',
            name='language',
            field=models.CharField(default=b'fr', max_length=255, verbose_name='language', db_index=True, choices=[(b'de', 'German'), (b'en', 'English'), (b'es', 'Spanish'), (b'fr', 'French')]),
        ),
    ]
