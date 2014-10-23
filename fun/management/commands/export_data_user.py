# -*- coding: utf-8 -*-

from datetime import datetime
import logging
from smtplib import SMTPRecipientsRefused

from django.db import models
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.conf import settings
from optparse import make_option
from django.db.models.query import QuerySet
from pprint import PrettyPrinter
from django.core.files import File
from django.template.loader import render_to_string
import json
from bson import json_util

import lms.lib.comment_client as cc
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from pymongo import MongoClient
from student.models import UserProfile

logger = logging.getLogger(__name__)


# to run it just do ~/edx-platform$ ./manage.py lms export_data_user --settings=fun.lms_sloop --username=the_username

class Command(BaseCommand):
    help = """
        Return all data concerning a user
        specify a user using --username=...
        Optionnaly you can specify a file to output with --file
        if not the filename will be export_theusername.log
        The output file will be store on /tmp

        ./manage.py lms export_data_user --settings=fun.lms_sloop --username=anonymized1 [--file=toto.txt]
        [--host=127.0.0.1][--user_mongo=user_for_mongo][--pwd_mongo=password_for_mongo]
        http://edx.readthedocs.org/en/latest/internal_data_formats/sql_schema.html
        http://edx.readthedocs.org/en/latest/internal_data_formats/discussion_data.html
    """
    option_list = BaseCommand.option_list + (
        make_option(
            "--username",
            dest="username",
            help="the username"
        ),
        make_option(
            "--file",
            dest="file",
            help="the file to write",
            default=""
        ),
        make_option(
            "--host",
            dest="host",
            help="the ip host adress for mongo connexion",
            default="127.0.0.1"
        ),
        make_option(
            "--user_mongo",
            dest="user_mongo",
            help="the username for mongo connexion",
            default=""
        ),
        make_option(
            "--pwd_mongo",
            dest="pwd_mongo",
            help="the password for mongo connexion",
            default=""
        ),
        make_option(
            "--email",
            dest="email",
            help="Send the result to the given email",
            default=False
        ),
    )

    def handle(self, *args, **options):
        if options['username'] is None:
            raise CommandError("Option `--username=...` must be specified.")
        if options['file'] is None or options['file'] == "":
            filename = "export_%s.log" % options['username']
        else:
            filename = options['file']
        filename = '/tmp/%s' % filename

        try:
            user = User.objects.get(username=options['username'])
            profile = UserProfile.objects.get(user=user)
        except:
            raise CommandError("User and/or profile with username `%s` not found." % options['username'])

        host = '127.0.0.1'
        if options['host']:
            host = options['host']
            print u"Using %s as host address" % host

        user_mongo = None
        password_mongo = None
        if options['user_mongo'] and options['user_mongo'] != "":
            user_mongo = options['user_mongo']
            password_mongo = options['pwd_mongo']
            print u"With user %s" % user_mongo

        #return all models found
        all_models = models.get_models(include_auto_created=True)
        with open(filename, 'wt') as f:
            my_file = File(f)
            printer = PrettyPrinter(stream=my_file, indent=2, width=1024, depth=None)
            #SQL DATA
            #TABLE USER:
            printer.pprint("Table User :")
            printer.pprint(to_dict(user, exclude=('id', 'User.password')))
            #TABLE USER PROFILE:
            printer.pprint("Table User profile :")
            printer.pprint(to_dict(profile))
            printer.pprint("--")
            #printer.pprint(to_dict(user, exclude=('id', 'User.password')))
            printer.pprint("--")
            #OTHER TABLE
            #parse all models to find which one has a foreign key with User
            for model in all_models:
                for field in model._meta.fields:
                    if field.get_internal_type() == "ForeignKey" and field.rel.to == User:
                        printer.pprint("Table %s :" % model.__name__)
                        #OR if isinstance(field, models.ForeignKey)
                        kwargs = {field.name: user}
                        qs = model.objects.select_related().filter(**kwargs)
                        if qs:
                            for q in qs:
                                #print to_dict(q, exclude=('id', 'User.password'))
                                printer.pprint(to_dict(q, exclude=('id', 'User.password')))
                                #http://palewi.re/posts/2009/09/04/django-recipe-pretty-print-objects-and-querysets/
                                #printer.pprint(qs)
                                #dprint(qs, stream=my_file, indent=1, width=80, depth=None)
                        else:
                            printer.pprint("No data found for this user")
                        printer.pprint("--")

            #MONGO DATA
            client = MongoClient(host=host)
            db = client.cs_comments_service
            if user_mongo:
                db.authenticate(user_mongo, password_mongo)
            list_post = db.contents.find({"author_id": "%s" % user.id})
            printer.pprint("Discussions :")
            printer.pprint("Nombre d'entree : %s" % list_post.count())
            for post in list_post:
                printer.pprint(post)

            printer.pprint(20 * "*")

        if options['email']:
            context = {}
            context['subject'] = u"[FUN] Export des données de l'utilisateur %s au %s" % (
                options['username'], datetime.now().strftime('%d/%m/%Y'))
            html_content = render_to_string('fun/emails/base_email.html', context)
            text_content = "This is a HTML only email"

            email = EmailMultiAlternatives(
                subject=context['subject'],
                body=text_content,
                from_email=settings.SERVER_EMAIL,
                to=[options['email']],
            )
            email.attach_alternative(html_content, "text/html")
            email.attach_file(filename)
            try:
                email.send()
            except SMTPRecipientsRefused:
                logger.error(u"Stat email could not be sent(%s)." % subject)
                print u"Unexpected error append while sending %s" % filename


def to_dict(obj, exclude=[]):
    """
    """
    tree = {}
    for field in obj._meta.fields + obj._meta.many_to_many:
        if field.name in exclude or \
                '%s.%s' % (type(obj).__name__, field.name) in exclude:
            continue
        try:
            value = getattr(obj, field.name)
        except obj.DoesNotExist:
            value = None

        if type(field) in [models.ForeignKey, models.OneToOneField]:
            #to_dict(value, exclude=exclude)
            tree[field.name] = "%s" % value
        elif isinstance(field, models.ManyToManyField):
            array_value = []
            for val in value.all():
                #to_dict(v, exclude=exclude))
                array_value.append(val)
            tree[field.name] = "%s" % array_value
        elif isinstance(field, models.DateTimeField):
            tree[field.name] = str(value)
        elif isinstance(field, models.FileField):
            tree[field.name] = {'url': value.url}
        else:
            tree[field.name] = value

    return tree
