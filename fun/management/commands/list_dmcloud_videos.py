#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
from xmodule.modulestore.django import modulestore

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        results = {}
        for course in modulestore().get_courses():
            if course.org not in results:
                results[course.org] = get_org(course.org)
            results[course.org]["courses"][unicode(course.id)] = get_course(course)
        print json.dumps(results, indent=4, sort_keys=True)

def get_org(org):
    from universities.models import University
    try:
        university = University.objects.get(code=org)
        dmcloud_user_id = university.dm_user_id
        dmcloud_api_key = university.dm_api_key
    except University.DoesNotExist:
        dmcloud_user_id = "N/A"
        dmcloud_api_key = "N/A"

    return {
        "courses": {},
        "dmcloud": {
            "user_id": dmcloud_user_id,
            "api_key": dmcloud_api_key,
        },
    }

def get_course(course):
    return {
        "videos": get_videos(course),
        "display_name": course.display_name,
    }

def get_videos(course):
    videos = []
    for item in modulestore().get_items(course.id):
        if item.category in ['video', 'dmcloud']:
            if item.id_video:
                videos.append({
                    "dmcloud_id": item.id_video,
                    "display_name": item.display_name
                })
    return videos
