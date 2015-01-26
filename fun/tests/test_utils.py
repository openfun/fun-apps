# -*- coding: utf-8 -*-
from django.test import TestCase
from django.template.base import TemplateDoesNotExist

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

class Template404CannotBeFoundTestCase(TestCase):

    def test_calling_non_existant_url_raises_error(self):
        # Whenever this test will fail, it will mean that Edx (or us) has fixed
        # the test configuration so that the 404.html template is found
        # whenever a 404 error is raised. When that will be the case, we will
        # be able to replace fun.utils.ensure_valid_course_key by its edx
        # synonym.
        self.assertRaises(
            TemplateDoesNotExist,
            self.client.get,
            "this-url-totally-does-not-exist"
        )
