# -*- coding: utf-8 -*-
import hashlib
import hmac
import json
import logging
from pprint import pprint

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Update FUN's course data."

    def update_user(self, users, batch):

        joanie_hooks = getattr(settings, "JOANIE_HOOKS")
        if not joanie_hooks:
            self.stdout.write("No hooks found")
            return

        users_hook = joanie_hooks.get('hooks', {}).get('users')
        if not users_hook:
            self.stdout.write("No users hook found")
            return

        data = {"users": []}
        for user in users:
            # self.stdout.write('.', ending='')

            data["users"].append({
                "username": user.username,
                "email": user.email,
                "password": user.password,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
                "date_joined": user.date_joined.isoformat(),
                "last_login": user.last_login.isoformat(),
            })

        self.stdout.write('Sending… ', ending='')
        json_data = json.dumps(data)
        # pprint(data)

        signature = hmac.new(
            joanie_hooks["secret"].encode("utf-8"),
            msg=json_data.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        try:
            response = requests.post(
                users_hook,
                json=data,
                headers={"Authorization": "SIG-HMAC-SHA256 {:s}".format(signature)},
                verify=joanie_hooks.get("verify", True),
                timeout=5
            )
        except requests.exceptions.ReadTimeout:
            logger.error(
                "Call to user hook timed out for batch {}/{}".format(*batch),
                # extra={"sent": data},
            )
            self.stdout.write("Error")
            return None

        if response.status_code != requests.codes.ok:
            # pprint(response.content)
            logger.error(
                "Call to user hook failed for batch {}/{}".format(*batch),
                extra={"response": response.content},
            )
            self.stdout.write("Error")
        else:
            self.stdout.write("Success")
        return None

    def handle(self, *args, **options):
        users_batch_size = 1000
        users_count = User.objects.all().count()
        for current_user_index in range(0, users_count, users_batch_size):
            users = User.objects.all()[
                current_user_index:current_user_index + users_batch_size
            ]
            self.stdout.write(
                'User {}-{}/{}: '.format(
                    current_user_index,
                    current_user_index + users_batch_size,
                    users_count
                ),
                ending=''
            )
            self.update_user(
                users,
                batch=(current_user_index, current_user_index + users_batch_size)
            )

        print("Done !!!")
