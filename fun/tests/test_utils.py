# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from courses.utils import get_about_section
from courses.views import get_dmcloud_url
from fun.tests.utils import skipUnlessCms
import fun.utils.html

class ParagraphText(TestCase):

    def test_first_paragraph_text(self):
        html = "<p>12345</p>"
        self.assertEqual("12345", fun.utils.html.first_paragraph_text(html))

    def test_first_paragraph_is_empty(self):
        html = """<p></p>
        
        <p>1234567890</p>"""
        self.assertEqual("1234567890", fun.utils.html.first_paragraph_text(html))

    def test_truncate_first_paragraph(self):
        self.assertEqual("12345", fun.utils.html.truncate_first_paragraph("<p>12345</p>", 5))
        self.assertEqual("...", fun.utils.html.truncate_first_paragraph("<p>12345</p>", 2))
        self.assertEqual("1...", fun.utils.html.truncate_first_paragraph("<p>12345</p>", 4))

@skipUnlessCms
class TestDmCloudVideoId(ModuleStoreTestCase):
    def test_dmcloud_public_id(self):
        """
        Tests that we always get a correct dailmotion id from the about section.
        The public video id is store in Mongo surrounded by an iframe tag referencing youtube.
        As we use dailmotion we need to extract the id from the iframe and create a
        new one referencing dailymotion (see function get_dmcloud_url).
        """
        from contentstore.views.course import settings_handler

        course = CourseFactory.create()
        instructor = InstructorFactory.create(course_key=course.id)
        self.client.login(username=instructor.username, password="test")

        dm_code = 'x2an9mg'
        course_details = {'intro_video' : dm_code}
        self.client.post(reverse(settings_handler,
                                 args=[str(course.id)]),
                         json.dumps(course_details),
                         content_type='application/json',
                         HTTP_ACCEPT='application/json')
        video_tag_youtube = get_about_section(course, 'video')
        self.assertIn(dm_code, video_tag_youtube)
        video_tag_dailymotion = '<iframe width="560" height="315" frameborder="0" scrolling="no" allowfullscreen="" src="//www.dailymotion.com/embed/video/' + dm_code + '"></iframe>'
        self.assertEqual(video_tag_dailymotion, get_dmcloud_url(course, video_tag_youtube))
