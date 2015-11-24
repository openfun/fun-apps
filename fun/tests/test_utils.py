# -*- coding: utf-8 -*-
import bs4
import json

from django.core.urlresolvers import reverse
from django.test import TestCase

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from courses.utils import get_about_section
from fun.utils import get_teaser
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
class TestDailymotionVideoId(ModuleStoreTestCase):
    def test_teaser_public_id(self):
        """
        Tests that we always get a correct dailymotion id from the about section.
        The public video id is store in Mongo surrounded by an iframe tag referencing youtube.
        As we use dailmotion we need to extract the id from the iframe and create a
        new one referencing dailymotion (see function get_teaser).
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

class TestDailymotionTeaser(TestCase):
    def test_get_teaser(self):
        video_id = 'abcd'
        teaser = get_teaser(video_id)
        soup = bs4.BeautifulSoup(teaser)
        iframe = soup.find('iframe')
        iframe_src = iframe.attrs.get('src')

        self.assertNotIn(
            "'", teaser,
            "A \"'\" character is dangerous as it will prevent the javascript code from parsing it correctly."
        )
        self.assertIsNotNone(iframe)
        self.assertIn("autoplay=1", iframe_src)
        self.assertIn(video_id, iframe_src)
