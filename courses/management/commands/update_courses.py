import random

from django.core.management.base import BaseCommand

from opaque_keys.edx.locator import CourseLocator
from xmodule.contentstore.content import StaticContent
from xmodule.modulestore.django import modulestore

from courses.models import Course
from courses.utils import get_about_section


class Command(BaseCommand):
    help = "Update FUN's course data."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.courses = modulestore().get_courses()
        self.courses_keys = [unicode(c.id) for c in self.courses]

    def get_course_score(self):
        return random.randint(1, 100)

    def get_course_title(self, course_descriptor):
        title = get_about_section(course_descriptor, 'title')
        return title or ''

    def get_course_description(self, course_descriptor):
        description = get_about_section(
            course_descriptor, 'short_description'
        )
        return description or ''

    def get_course_image_url(self, course_descriptor):
        key = unicode(course_descriptor.id)
        course_locator = CourseLocator.from_string(key)
        location = StaticContent.compute_location(
            course_locator, course_descriptor.course_image
        )
        return location.to_deprecated_string()

    def update_course_data(self):
        '''
        For each course found in Mongo database, we create or update
        the corresponding course in SQL Course table.
        '''
        for mongo_course in self.courses:
            key = unicode(mongo_course.id)
            self.stdout.write('\n Updating data for course {}'.format(key))
            course, was_created =  Course.objects.get_or_create(key=key)
            if course.prevent_auto_update:
                self.stdout.write('\n Skipping updates for {}'.format(key))
                continue
            if was_created:
                course.is_active = True
            course.title = self.get_course_title(mongo_course)
            course.short_description = self.get_course_description(mongo_course)
            course.image_url = self.get_course_image_url(mongo_course)
            course.score = self.get_course_score()
            course.start_date = mongo_course.start
            course.end_date = mongo_course.end
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
