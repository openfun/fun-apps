# -*- coding: utf-8 -*-

import datetime
import dateutil.parser
import json
import logging
import requests
import pytz

from django.conf import settings
from django.utils import timezone

from optparse import make_option

from django.core.management.base import BaseCommand

from ...utils import connect_and_drop_collection, COLLECTION


logger = logging.getLogger(__name__)

ZENDESK_BASE_API = 'https://fun1.zendesk.com'


class Command(BaseCommand):
    help = """Retrieve from Zendesk API the student FAQ and store it to mongo so we can display it on website.
    """
    option_list = BaseCommand.option_list + (
        make_option('-l', '--log',
                    action='store_true',
                    dest='log',
                    default=False),
        make_option('-d', '--dry-run',
                    action='store_true',
                    dest='dry_run',
                    default=False),
        make_option('-u', '--username',
                    action='store',
                    dest='username',
                    type='string'),
        make_option('-t', '--token',
                    action='store',
                    dest='token',
                    type='string'),
                    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self._log = False
        self.username = ''
        self.token = ''

    def _query_zendesk(self, url):
        response = requests.get(ZENDESK_BASE_API + url,
                auth=(self.username + "/token", self.token))
        data = json.loads(response.content)
        return data

    def log(self, message):
        if self._log:
            logger.info(message)

    def handle(self, *args, **options):

        self._log = options['log']
        try:
            self.username = options['username'] or settings.ZENDESK_USERNAME
            self.token = options['username'] or settings.ZENDESK_TOKEN
        except AttributeError:
            logger.error("Can't connect to Zendesk API: credentials missing")
            return

        collection = connect_and_drop_collection(COLLECTION)

        categories = self._query_zendesk('/api/v2/help_center/categories.json')

        for category in categories['categories']:
            self.log("%s\n" % category['name'])

            sections = self._query_zendesk('/api/v2/help_center/categories/{id}/sections.json'.format(
                    id=category['id']))
            for section in sections['sections']:
                self.log("%s\n" % section['name'])

                articles = self._query_zendesk('/api/v2/help_center/sections/{id}/articles.json'.format(
                        id=section['id']))

                last_document_update = datetime.datetime(1970, 1, 1).replace(
                        tzinfo=pytz.timezone('UTC'))  # initialize with a date in the far past

                for article in articles['articles']:
                    self.log("%s\n" % article['name'])

                    updated_at = dateutil.parser.parse(article['updated_at'])
                    if updated_at > last_document_update:
                        last_document_update = updated_at

                    item = {
                        'id': article['id'],
                        'category': {
                            'id': category['id'],
                            'name': category['name'],
                            'position': category['position']
                        },
                        'section': {
                            'id': section['id'],
                            'name': section['name'],
                            'position': section['position']
                        },
                        'name': article['name'],
                        'udated_at': updated_at,
                        'body': article['body'],
                        'last_update': timezone.now(),  # This is the last time we successuly fetched Zendesk API
                        'last_document_update': last_document_update,  # This is the lastest document update
                    }

                    if not options['dry_run']:
                        collection.insert(item)

        self.log('\n\n%d categories %d sections, %d articles\n' % (
                collection.count(),
                len(list(collection.distinct('category'))),
                len(list(collection.distinct('section')))
                ))
