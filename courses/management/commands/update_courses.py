import optparse
import StringIO

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify

from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.files import get_thumbnailer

from courseware.courses import get_course_about_section
from opaque_keys.edx.locator import CourseLocator
from opaque_keys import InvalidKeyError
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.exceptions import NotFoundError
from xmodule.modulestore.django import modulestore

from courses import settings as courses_settings
from courses.models import Course, CourseUniversityRelation
from universities.models import University


class CourseHandler(object):

    def __init__(self, course_descriptor):
        self.course_descriptor = course_descriptor
        self.key = unicode(course_descriptor.id)

    @property
    def memory_image_file(self):
        try:
            asset_location = StaticContent.get_location_from_path(self.image_url)
            content = contentstore().find(asset_location, as_stream=True)
        except (NotFoundError, InvalidKeyError):
            return None
        image_file = StringIO.StringIO(content.copy_to_in_mem().data)
        return image_file

    @property
    def title(self):
        title = get_course_about_section(self.course_descriptor, 'title')
        return title or ''

    @property
    def university_name(self):
        name = ''
        if self.course_descriptor.display_organization:
            name = unicode(self.course_descriptor.display_organization)
        return name

    @property
    def image_location(self):
        course_locator = CourseLocator.from_string(self.key)
        location = StaticContent.compute_location(
            course_locator, self.course_descriptor.course_image
        )
        return location

    @property
    def image_url(self):
        location = self.image_location
        url = unicode(location)
        return url

    def make_thumbnail(self, options):
        if not self.memory_image_file:
            return None
        base_filename = slugify(self.key)
        try:
            thumbnail = get_thumbnailer(
                self.memory_image_file,
                relative_name='courses-thumbnails/{}'.format(base_filename)
            ).get_thumbnail(options)
        except InvalidImageFormatError:
            thumbnail = None
        return thumbnail

    def get_university(self):
        try:
            university = University.objects.get(code=self.course_descriptor.org)
        except University.DoesNotExist:
            university = None
        return university

    def assign_university(self, course):
        university = self.get_university()
        assigned = False
        if university:
            try:
                CourseUniversityRelation.objects.create(
                    course=course,
                    university=university
                )
                assigned = True
            except IntegrityError:
                pass
        return assigned


class Command(BaseCommand):
    help = "Update FUN's course data."
    option_list = BaseCommand.option_list + (
        optparse.make_option('--force-universities-assignment',
            action='store_true',
            dest='assign_universities',
            default=False,
            help='Force university assignment on existing courses.'),
    )

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.courses = modulestore().get_courses()
        self.courses_keys = [unicode(c.id) for c in self.courses]


    def update_course_data(self, *args, **options):
        '''
        For each course found in Mongo database, we create or update
        the corresponding course in SQL Course table.
        '''
        assign_universities = options['assign_universities']
        for mongo_course in self.courses:
            course_handler = CourseHandler(mongo_course)
            key = course_handler.key
            self.stdout.write('Updating data for course {}\n'.format(key))
            course, was_created = Course.objects.get_or_create(key=key)
            if course.prevent_auto_update:
                self.stdout.write(' Skipping updates for {}\n'.format(key))
                continue
            if was_created or assign_universities:
                university = course_handler.assign_university(course)
                if university:
                    self.stdout.write('\n\t University assigned '
                    'to "{}"'.format(key))
                else:
                    self.stdout.write('\n\t No university assigned '
                    'to {}'.format(key))
            course.is_active = True
            course.show_in_catalog = bool(mongo_course.ispublic)
            course.university_display_name = course_handler.university_name
            course.title = course_handler.title
            course.image_url = course_handler.image_url
            thumbnails_info = {}
            for thumbnail_alias, thumbnails_options in \
                    courses_settings.FUN_THUMBNAIL_OPTIONS.items():
                thumbnail = course_handler.make_thumbnail(thumbnails_options)
                if thumbnail:
                    thumbnails_info[thumbnail_alias] = thumbnail.url
            course.thumbnails_info = thumbnails_info
            course.start_date = mongo_course.start
            course.end_date = mongo_course.end
            course.save()
        return None

    def deactivate_orphan_courses(self, *args, **options):
        '''
        Orphan courses are entries that exist in SQL Course table while the
        corresponding Mongo courses are not listed anymore. This method deactivate
        orphan courses.
        '''
        orphan_courses = Course.objects.exclude(key__in=self.courses_keys)
        orphan_courses.update(is_active=False)
        self.stdout.write('Deactivated {} orphan courses\n'.format(orphan_courses.count()))
        return None

    def handle(self, *args, **options):
        self.update_course_data(*args, **options)
        self.deactivate_orphan_courses(*args, **options)
        self.stdout.write('\n Updated courses {}\n'.format(len(self.courses)))
