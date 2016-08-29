from datetime import datetime

from django.test import TestCase
from mock import patch

from xmodule.modulestore.django import modulestore as real_modulestore
from xmodule.course_module import CATALOG_VISIBILITY_CATALOG_AND_ABOUT, CATALOG_VISIBILITY_NONE
from django.core.management import call_command

from courses.models import Course


class MockModuleStore():
    def __init__(self, course):
        self.course = course

    def get_course(self, _):
        return self.course


class TestSqlDuplication(TestCase):
    @patch("xmodule.modulestore.django.modulestore")
    def test_updates_values_in_mongo_should_be_updated_in_sql(self, mock_modulestore):
        mongo_courses = real_modulestore().get_courses()
        mongo_course = mongo_courses[0] if mongo_courses else None

        date = datetime.fromtimestamp(200000)
        visibility = {True: CATALOG_VISIBILITY_CATALOG_AND_ABOUT, False: CATALOG_VISIBILITY_NONE}

        if mongo_course:
            catalog_visibility = not mongo_course.catalog_visibility.lower() == CATALOG_VISIBILITY_CATALOG_AND_ABOUT
            mongo_course.catalog_visibility = visibility[catalog_visibility]
            mongo_course.start = date
            course_id = unicode(mongo_course.id)

            mock_modulestore.return_value = MockModuleStore(mongo_course)
            call_command('update_courses', course_id=course_id)

            fun_course = Course.objects.get(key=course_id)
            self.assertEqual(1970, fun_course.start_date.year)
            self.assertEqual(catalog_visibility, fun_course.show_in_catalog)
