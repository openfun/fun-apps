# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20180705_1154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='translatedterms',
            name='tr_text',
            field=models.TextField(default=b"\n.. Ce champs est dans un format ReST (comme un wiki)\n.. Ceci est un commentaire\n.. http://deusyss.developpez.com/tutoriels/Python/SphinxDoc/#LIV-G\n\n\n.. Les 4 lignes finales (honor, privacy, tos, legal)\n.. permettent la navigation dans le contrat au niveau des ancres\n.. Pri\xc3\xa8re de les ins\xc3\xa9rer avant les titres correspondant\n.. honor = Charte utilisateurs\n.. privacy = Politique de confidentialit\xc3\xa9\n.. tos = Conditions g\xc3\xa9n\xc3\xa9rales d'utilisation\n.. legal =  Mentions l\xc3\xa9gales\n\n.. Ces commentaires ci dessus peuvent \xc3\xaatre retir\xc3\xa9s\n.. ils sont juste l\xc3\xa0 comme aide m\xc3\xa9moire :)\n\n\n.. _honor:\n\n.. _privacy:\n\n.. _tos:\n\n.. _legal:\n\n", verbose_name='Terms and conditions. (ReStructured Text)'),
        ),
    ]
