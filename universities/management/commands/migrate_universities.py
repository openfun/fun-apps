# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import json
import logging
import optparse

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from universities.models import University

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Migrate university to Joanie's Organization."
    option_list = BaseCommand.option_list + (
        optparse.make_option(
            '--university-id',
            action='store',
            type='string',
            dest='university_id',
            default='',
            help='Migrate only the given university.',
        ),
    )

    def update_all_universities(self, universities):
        '''
        For each university, we create or update the corresponding
        university in SQL University table.
        '''
        for university in universities:
            self.update_university(university)

        self.stdout.write('Number of universities parsed: {}\n'.format(len(universities)))
        return None

    def update_university(self, university):
        '''
        For the given university, we create or update the corresponding
        university in SQL University table.
        '''

        key = unicode(university.id)
        self.stdout.write('\nMigrating data for university {}\n'.format(key))

        joanie_hooks = getattr(settings, "JOANIE_HOOKS")
        if not joanie_hooks:
            return

        universities_hook = joanie_hooks.get('hooks', {}).get('universities')
        if not universities_hook:
            return

        logo = base64.b64encode(university.logo.file.read())
        data = {
            "code": university.code,
            "title": university.name,
            "logo_base64": logo,
            "logo_name": university.logo.name,
        }

        json_data = json.dumps(data)
        signature = hmac.new(
            joanie_hooks["secret"].encode("utf-8"),
            msg=json_data.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        response = requests.post(
            universities_hook,
            json=data,
            headers={"Authorization": "SIG-HMAC-SHA256 {:s}".format(signature)},
            verify=joanie_hooks.get("verify", True),
        )

        if response.status_code != requests.codes.ok:
            logger.error(
                "Call to course hook failed for {:s}".format(key),
                extra={"sent": data, "response": response.content},
            )
            return None

        self.stdout.write('Migrated university {}\n'.format(key))
        return None

    def handle(self, *args, **options):
        university_id = options.get('university_id')
        if university_id:
            university = University.objects.get(id=university_id)
            self.update_university(
                university=university,
            )
        else:
            universities = University.objects.all()
            self.update_all_universities(
                universities=universities,
            )

        print "Done !!!"
