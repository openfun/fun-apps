# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TermsAndConditions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name', db_index=True)),
                ('version', models.CharField(max_length=12, verbose_name='Terms and conditions version (semver)')),
                ('datetime', models.DateTimeField(auto_now_add=True, verbose_name='Acceptance date', db_index=True)),
                ('text', models.TextField(verbose_name='Terms and conditions content (HTML allowed)')),
            ],
            options={
                'ordering': ['name', '-datetime'],
                'verbose_name': 'Terms and conditions',
                'verbose_name_plural': 'Terms and conditions',
            },
        ),
        migrations.CreateModel(
            name='UserAcceptance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('datetime', models.DateTimeField(auto_now=True, verbose_name='Acceptance date', db_index=True)),
                ('terms', models.ForeignKey(related_name='accepted', to='payment.TermsAndConditions')),
                ('user', models.ForeignKey(related_name='terms_accepted', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'User terms and conditions acceptance',
            },
        ),
        migrations.AlterUniqueTogether(
            name='useracceptance',
            unique_together=set([('user', 'terms')]),
        ),
    ]
