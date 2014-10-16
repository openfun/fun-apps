# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core import serializers
#from sys import argv

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.db.models.query import QuerySet
from pprint import PrettyPrinter
from django.core.files import File


#to run it just do $>./manage.py lms export_data_user --settings=fun.lms_sloop

class Command(BaseCommand):
    help = """
        Return all data concerning a user
        specify a user using --username=...
        Optionnaly you can specify a file to output with --file
        The output file will be store on /tmp
        
        ./manage.py lms export_data_user --settings=fun.lms_sloop --username=anonymized1 [--file=toto.txt]
        
    """
    option_list = BaseCommand.option_list + (
        make_option(
            "-u", 
            "--username", 
            dest = "username",
            help = "the username"
        ),
        make_option(
            "-f", 
            "--file", 
            dest = "file",
            help = "the file to write"
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
        
        all_models = models.get_models(include_auto_created=True) #return all models found
        
        with open('/tmp/%s'%filename, 'wt') as f:
            myfile = File(f)
            printer = PrettyPrinter(stream=myfile, indent=2, width=180, depth=None)
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
                                #printer.pprint(qs)
                                #dprint(qs, stream=myfile, indent=1, width=80, depth=None)
                        else:
                            printer.pprint("No data found for this user")
                        printer.pprint("--")   
        


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

def dprint(object, stream=None, indent=1, width=80, depth=None):
    """
    A small addition to pprint that converts any Django model objects to dictionaries so they print prettier.

    h3. Example usage

        >>> from toolbox.dprint import dprint
        >>> from app.models import Dummy
        >>> dprint(Dummy.objects.all().latest())
            {'first_name': u'Ben',
            'last_name': u'Welsh',
            'city': u'Los Angeles',
            'slug': u'ben-welsh',
    """
    # Catch any singleton Django model object that might get passed in
    if getattr(object, '__metaclass__', None):
        if object.__metaclass__.__name__ == 'ModelBase':
            # Convert it to a dictionary
            object = object.__dict__
    
    # Catch any Django QuerySets that might get passed in
    elif isinstance(object, QuerySet):
        # Convert it to a list of dictionaries
        object = [i.__dict__ for i in object]
        
    # Pass everything through pprint in the typical way
    printer = PrettyPrinter(stream=stream, indent=indent, width=width, depth=depth)
    printer.pprint(object)

