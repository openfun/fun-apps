# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import serializers

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.db.models.query import QuerySet
from pprint import PrettyPrinter
from django.core.files import File
import json
from bson import json_util

import lms.lib.comment_client as cc
from opaque_keys.edx.locations import SlashSeparatedCourseKey
from pymongo import MongoClient

#to run it just do ~/edx-platform$ ./manage.py lms export_data_user --settings=fun.lms_sloop --username=the_username

class Command(BaseCommand):
    help = """
        Return all data concerning a user
        specify a user using --username=...
        Optionnaly you can specify a file to output with --file
        The output file will be store on /tmp
        
        ./manage.py lms export_data_user --settings=fun.lms_sloop --username=anonymized1 [--file=toto.txt]
        [--host=127.0.0.1][--user_mongo=user_for_mongo][--pwd_mongo=password_for_mongo]
        http://edx.readthedocs.org/en/latest/internal_data_formats/sql_schema.html
        http://edx.readthedocs.org/en/latest/internal_data_formats/discussion_data.html
        
    """
    option_list = BaseCommand.option_list + (
        make_option(
            "--username", 
            dest = "username",
            help = "the username"
        ),
        make_option(
            "--file", 
            dest = "file",
            help = "the file to write"
        ),
        make_option(
            "--host", 
            dest = "host",
            help = "the ip host adress for mongo connexion"
        ),
        make_option( 
            "--user_mongo", 
            dest = "user_mongo",
            help = "the username for mongo connexion"
        ),
        make_option( 
            "--pwd_mongo", 
            dest = "pwd_mongo",
            help = "the password for mongo connexion"
        ),
    )
        
        
        
    def handle(self, *args, **options):
        if options['username'] == None :
            raise CommandError("Option `--username=...` must be specified.")
        filename = ""
        if options['file'] == None :
            filename = "export_%s.log" %options['username']
        else:
            filename = options['file']
            #raise CommandError("Option `--file=...` must be specified.")
        try:
            finduser = User.objects.get(username=options['username'])
        except:
            raise CommandError("User with username `%s` not found." %options['username'])
        
        host = '127.0.0.1'
        if options['host']:
            host=options['host']
            print u"Using %s as host address" %host
        
        
        user_mongo = None
        password_mongo = None
        if options['user_mongo']:
            user_mongo=options['user_mongo']
            password_mongo=options['pwd_mongo']
            print u"With user %s" % user_mongo
        
        all_models = models.get_models(include_auto_created=True) #return all models found
        
        with open('/tmp/%s'%filename, 'wt') as f:
            myfile = File(f)
            printer = PrettyPrinter(stream=myfile, indent=2, width=1024, depth=None)
            #SQL DATA
            #TABLE USER:
            printer.pprint("Table User :")
            printer.pprint(to_dict(finduser, exclude=('id', 'User.password')))
            printer.pprint("--")
            #OTHER TABLE
            for model in all_models: #parse all models to find which one has a foreign key with User
                for field in model._meta.fields:
                    if field.get_internal_type()=="ForeignKey" and field.rel.to==User: 
                        printer.pprint("Table %s :" %model.__name__)
                        #OR if isinstance(field, models.ForeignKey)
                        kwargs = {field.name:finduser}
                        qs = model.objects.select_related().filter(**kwargs) #.values()
                        if qs:
                            for q in qs:
                                #print to_dict(q, exclude=('id', 'User.password'))
                                printer.pprint(to_dict(q, exclude=('id', 'User.password'))) 
                                #http://palewi.re/posts/2009/09/04/django-recipe-pretty-print-objects-and-querysets/
                                #printer.pprint(qs)
                                #dprint(qs, stream=myfile, indent=1, width=80, depth=None)
                        else:
                            printer.pprint("No data found for this user")
                        printer.pprint("--")   
            
            #MONGO DATA
            client = MongoClient(host=host)
            db = client.cs_comments_service
            if user_mongo:
                db.authenticate(user_mongo, password_mongo)
            listpost = db.contents.find({"author_id":"%s" %finduser.id})
            printer.pprint("Discussions :")
            printer.pprint("Nombre d'entree : %s" %listpost.count())
            for post in listpost:
                printer.pprint("%s" %json.dumps(post, indent=4, default=json_util.default))
                #printer.pprint(post)
                printer.pprint("--")
            printer.pprint(20*"*")


def to_dict(obj, exclude=[]):
    """
    """
    tree = {}
    for field in obj._meta.fields + obj._meta.many_to_many:
        if field.name in exclude or \
           '%s.%s' % (type(obj).__name__, field.name) in exclude:
            continue
        
        try :
            value = getattr(obj, field.name)
        except obj.DoesNotExist:
            value = None

        if type(field) in [models.ForeignKey, models.OneToOneField]:
            tree[field.name] = "%s" %value #to_dict(value, exclude=exclude)
        elif isinstance(field, models.ManyToManyField):
            vs = []
            for v in value.all():
                vs.append(v) #to_dict(v, exclude=exclude))
            tree[field.name] = "%s" %vs
        elif isinstance(field, models.DateTimeField):
            tree[field.name] = str(value)
        elif isinstance(field, models.FileField):
            tree[field.name] = {'url': value.url}
        else:
            tree[field.name] = value

    return tree


"""
#cc_user = cc.User.from_django_user(finduser)
#cc_user.retrieve()
#default_query_params['sort_key'] = cc_user.get('default_sort_key') or default_query_params['sort_key']
course_key = SlashSeparatedCourseKey.from_deprecated_string("Bordeaux3/07001/Trimestre_1_2014") #course_id
profiled_user = cc.User(id=finduser.id, course_id=course_key)

query_params = {
    'page': 1,
    'per_page': 20,   # more than threads_per_page to show more activities
}

#try:
#    group_id = get_group_id_for_comments_service(request, course_key)
#except ValueError:
#    return HttpResponseBadRequest("Invalid group_id")
#if group_id is not None:
#    query_params['group_id'] = group_id

threads, page, num_pages = profiled_user.active_threads(query_params)
print 20*"*"
print len(threads), page, num_pages
print threads[0]
print 20*"*"
"""
"""
course_key = SlashSeparatedCourseKey.from_deprecated_string("Bordeaux3/07001/Trimestre_1_2014") #course_id
default_query_params = {
    'page': 1,
    'per_page': 20,
    'sort_key': 'date',
    'sort_order': 'desc',
    'text': '',
    'commentable_id': None,
    'course_id': course_key.to_deprecated_string(),
    'user_id': finduser.id,
    'group_id': None, #get_group_id_for_comments_service(request, course_key, discussion_id),  # may raise ValueError
}

threads, page, num_pages, corrected_text = cc.Thread.search(default_query_params)
print len(threads), page, num_pages
"""
#for thread in threads:
#    print thread
