# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import migrations, models

from xmodule.course_module import CATALOG_VISIBILITY_CATALOG_AND_ABOUT, CATALOG_VISIBILITY_NONE
from xmodule.modulestore.django import modulestore

from courses.models import Course


def update_visibility(mongo_course, visibility, user_id):
    if mongo_course.catalog_visibility != visibility:
        mongo_course.catalog_visibility = visibility
        modulestore().update_item(mongo_course, user_id)


def get_first_superuser():
    """Returns first superuser or None."""
    first_superuser = User.objects.filter(is_superuser=True).first()
    return first_superuser


def reversed_update(apps, schema_editor):
    """ reverse the migration : we put the mongo value to the default value (ie : CATALOG_VISIBILITY_CATALOG_AND_ABOUT)"""

    mongo_courses = modulestore().get_courses()

    # we need a superuser to manipulate mongo. Nevertheless, if there is none, there are no data in the base, so we don't need to make the migration
    user = get_first_superuser()
    if user:
        user_id = user.id

        for mongo_course in mongo_courses:
            visibility = CATALOG_VISIBILITY_CATALOG_AND_ABOUT
            update_visibility(mongo_course, visibility, user_id)


def update_mongo_courses(apps, schema_editor):
    """ Update the mongo "course_visibility" parameter from the SQL value in the FUN database.
    This is needed because the default value of course_visibility doesn't take account of the show_in_catalog value.
    """

    mongo_courses = modulestore().get_courses()

    # we need a superuser to manipulate mongo. Nevertheless, if there is none, there are no data in the base, so we don't need to make the migration
    user = get_first_superuser()
    if user:
        user_id = user.id

        fun_courses = Course.objects.all()

        for mongo_course in mongo_courses:
            course_id = mongo_course.id
            print("updating {}".format(course_id))

            try:
                fun_course = fun_courses.get(key=course_id)
            except Course.DoesNotExist:
                pass
                # if course is not found in fun, we let the default values in mongo
                print("course not found {}".format(course_id))
            else:
                visibility = CATALOG_VISIBILITY_NONE
                if fun_course.show_in_catalog:
                    visibility = CATALOG_VISIBILITY_CATALOG_AND_ABOUT
                update_visibility(mongo_course, visibility, user_id)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_mongo_courses, reversed_update),
    ]
