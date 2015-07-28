# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import datetime

from django.core.urlresolvers import reverse

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase

from fun.tests.utils import skipUnlessLms

from ..utils import connect_to_mongo, COLLECTION

now = datetime.datetime.now()
article = {
    "category": {"position": 1, "id": 1, "name": "Category name 1"},
    "body": "Article body 1",
    "name": "Article 1",
    "udated_at": now,
    "section": {"position": 1, "id": 1, "name": "Section 1"},
    "last_document_update": now,
    "id": 1,
    "last_update": now
}


@skipUnlessLms
class FAQTest(ModuleStoreTestCase):
    def setUp(self):
        super(FAQTest, self).setUp()
        db = connect_to_mongo()
        db[COLLECTION].insert(article)

    def test_faq_index(self):
        response = self.client.get(reverse('faq:index'))
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Category name 1",
                soup.find('ul', class_='faq-categories').find('h1').text)
        self.assertEqual(u"Section 1",
                soup.find('ul', class_='faq-categories').find('h2').text)
        self.assertEqual(u"Article 1",
                soup.find('ul', class_='faq-categories').find('a', class_='article').text)

    def test_faq_article(self):
        response = self.client.get(reverse('faq:article', args=[1]))
        self.assertEqual(200, response.status_code)

        soup = BeautifulSoup(response.content)
        self.assertEqual(u"Article 1",
                soup.find('div', class_='article').find('h1').text)
        self.assertEqual(u"Article body 1",
                soup.find('div', class_='article').find('p').text.strip())


