# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('universities', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='university',
            options={'ordering': ('-score', 'id'), 'verbose_name': 'University', 'verbose_name_plural': 'Universities'},
        ),
    ]
