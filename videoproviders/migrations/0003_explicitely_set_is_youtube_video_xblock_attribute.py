# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def set_is_youtube_video_fields(apps, schema_editor):
    """
    Update video xblocks for all courses. Since the is_youtube_video field is
    set to False by default, it is often not stored in Mongodb. This prevents
    us from changing the default value for this field. To avoid this problem,
    we explicitely set the value of this field in mongodb.
    """
    import xmodule.modulestore.django
    modulestore = xmodule.modulestore.django.modulestore()
    for course in modulestore.get_courses():
        course_store = modulestore._get_modulestore_for_courselike(course.id)
        if not hasattr(course_store, "collection"):
            # Course is not stored in mongodb
            continue
        course_store.collection.update(
            {"_id.category": 'video', "metadata.is_youtube_video": {"$exists": False}},
            {"$set": {"metadata.is_youtube_video": False}}
        )

def unset_is_youtube_video_fields(apps, schema_editor):
    """
    There is no need for a reverse mligration.
    """
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('videoproviders', '0002_videouploaderdeactivationperiod_youtubeauth_youtubecoursesettings'),
    ]

    operations = [
        migrations.RunPython(set_is_youtube_video_fields, reverse_code=unset_is_youtube_video_fields),
    ]
