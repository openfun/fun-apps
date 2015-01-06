# -*- coding: utf-8 -*-
from django.test import TestCase

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
