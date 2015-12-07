# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError


from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from fun.utils import funwiki

class Command(BaseCommand):

    help = """Remove write authorizations from all wiki articles from the given
courses. This should be doable via the wiki settings view, but a bug in
django-wiki prevents inheriting read/write permission changes.
"""
    args = "<course_id_1> <course_id_2>..."

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("Define at least one course_id argument")

        for course_key_string in args:
            course_key = CourseKey.from_string(course_key_string)
            course = modulestore().get_course(course_key)
            if course:
                urlpaths = funwiki.set_permissions(course, False)

                if not urlpaths:
                    self.stdout.write("---- Wiki root article for course {} could not be found\n".format(
                            course_key_string))
                else:
                    self.stdout.write("++++ Write permissions removed from wiki for course {}\n".format(
                            course_key_string))
            else:
                self.stdout.write("---- No course with key {}\n".format(course_key_string))
