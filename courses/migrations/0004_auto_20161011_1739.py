# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_default_value_to_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='subjects',
            field=models.ManyToManyField(related_name='courses', to='courses.CourseSubject', blank=True),
        ),
    ]
