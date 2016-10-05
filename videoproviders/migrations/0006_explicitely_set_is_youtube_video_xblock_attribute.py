# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_is_youtube_video_fields(apps, schema_editor):
    """
    This is the same migration as 0003, except that we switch the default value
    of the is_youtube_video field back to False. XBlocks for which the field is
    not explicitely defined need to be explicitely set to Youtube.
    """
    import xmodule.modulestore.django
    modulestore = xmodule.modulestore.django.modulestore()
    for course in modulestore.get_courses():
        course_store = modulestore._get_modulestore_for_courselike(course.id)
        if not hasattr(course_store, "collection"):
            # Course is not stored in mongodb
            continue
        for category in ['video', 'libcast_xblock']:
            course_store.collection.update(
                {"_id.category": category, "metadata.is_youtube_video": {"$exists": False}},
                {"$set": {"metadata.is_youtube_video": True}}
            )

def unset_is_youtube_video_fields(apps, schema_editor):
    """
    There is no need for a reverse mligration.
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('videoproviders', '0005_videofrontauth_videofrontcoursesettings'),
    ]

    operations = [
        migrations.RunPython(set_is_youtube_video_fields, reverse_code=unset_is_youtube_video_fields),
    ]
