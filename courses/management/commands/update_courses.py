import random

from django.core.management.base import BaseCommand

from xmodule.modulestore.django import modulestore

from courses.models import Course


class Command(BaseCommand):
    help = "Update FUN's course data."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.courses = modulestore().get_courses()
        self.courses_keys = [unicode(c.id) for c in self.courses]

    def get_course_score(self):
        return random.randint(1, 100)

    def find_out_if_course_is_new(self):
        return random.choice([True, False])

    def find_out_if_course_is_on_demand(self):
        return random.choice([True, False])

    def update_course_data(self):
        '''
        For each course found in Mongo database, we create or update
        the corresponding course in SQL Course table.
        '''
        for mongo_course in self.courses:
            key = unicode(mongo_course.id)
            self.stdout.write('\n Updating data for course {}'.format(key))
            course,_ =  Course.objects.get_or_create(key=key)
            if course.prevent_auto_update:
                self.stdout.write('\n Skipping updates for {}'.format(key))
                continue
            course.score = self.get_course_score()
            course.start_date = mongo_course.start
            course.end_date = mongo_course.end
            course.is_new = self.find_out_if_course_is_new()
            course.on_demand = self.find_out_if_course_is_on_demand()
            course.save()
        return None

    def deactivate_orphan_courses(self):
        '''
        Orphan courses are entries that exist in SQL Course table while the
        corresponding Mongo courses are not listed anymore. This method deactivate
        orphan courses.
        '''
        orphan_courses = Course.objects.exclude(key__in=self.courses_keys)
        orphan_courses.update(is_active=False)
        self.stdout.write('\n Deactivated {} orphan courses'.format(orphan_courses.count()))
        return None

    def handle(self, *args, **options):
        self.update_course_data()
        self.deactivate_orphan_courses()
        self.stdout.write('\n Updated courses {}'.format(len(self.courses)))
