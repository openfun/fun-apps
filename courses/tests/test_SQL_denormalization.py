from datetime import datetime

from django.test import TestCase
from mock import patch

from xmodule.modulestore.django import modulestore as real_modulestore
from xmodule.course_module import CATALOG_VISIBILITY_CATALOG_AND_ABOUT, CATALOG_VISIBILITY_NONE
from django.core.management import call_command

from openedx.core.djangoapps.models.course_details import CourseDetails

from courses.models import Course as FUNCourse

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory


class TestSqlDuplication(ModuleStoreTestCase, TestCase):
    def test_updates_values_in_mongo_should_be_updated_in_sql(self):
        """ Test that a already existing course is correctly updated
            by update_course management command.
        """
        mongo_course = CourseFactory.create(short_description='test')
        # short_description field is required by FUN Course model
        CourseDetails.update_about_item(
            mongo_course, 'short_description', u"Short description", None)

        self.assertFalse(FUNCourse.objects.all().exists())
        call_command('update_courses', course_id=unicode(mongo_course.id))

        self.assertTrue(u"Short description",
            FUNCourse.objects.get(key=mongo_course.id).short_description)

        CourseDetails.update_about_item(
            mongo_course, 'short_description', u"Short description changed",
            None)
        call_command('update_courses', course_id=unicode(mongo_course.id))

        self.assertEqual(
            u"Short description changed",
            FUNCourse.objects.get(key=mongo_course.id).short_description)
