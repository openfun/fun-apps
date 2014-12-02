# -*- coding: utf-8 -*-
from django.test import TestCase

import fun.utils.html

class ArticleImageTest(TestCase):

    def test_no_image_in_article(self):
        text = "This is a text"
        self.assertEqual("", fun.utils.html.first_image_src(text))

    def test_image_in_article(self):
        text = "This is a text with a image! <img src='pouac.html'>. And this is the rest of the text."
        img_src = fun.utils.html.first_image_src(text)
        self.assertEqual('pouac.html', img_src)

    def test_image_with_styling(self):
        html = """<img alt="" src="/media/2014/11/20/penguin.jpg" style="width: 800px; height: 532px;" />"""
        image = fun.utils.html.first_image(html)
        self.assertEqual("width: 800px; height: 532px;", image['style'])

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
