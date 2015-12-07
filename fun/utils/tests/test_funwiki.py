# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class TestWikiUtils(ModuleStoreTestCase):

    def setUp(self):
        super(TestWikiUtils, self).setUp()
        from course_wiki.views import get_or_create_root
        from wiki.models.urlpath import URLPath
        self.wiki_root = get_or_create_root()
        self.course = CourseFactory.create(org='ORG', display_name='COURSE', number='RUN')
        self.wiki_course_root = URLPath.create_article(self.wiki_root, 'RUN', title=u"Page 0")
        self.page1 = URLPath.create_article(self.wiki_course_root, 'page1', title=u"Page 1")
        self.page2 = URLPath.create_article(self.wiki_course_root, 'page2', title=u"page 2")
        self.page11 = URLPath.create_article(self.page1, 'page11', title=u"page 1.1")
        self.page111 = URLPath.create_article(self.page11, 'page111', title=u"page 1.1.1")
        self.page112 = URLPath.create_article(self.page11, 'page112', title=u"page 1.1.2")

    def test_base_page(self):
        from fun.utils import funwiki
        base_page = funwiki.get_base_page(self.course)
        self.assertEqual(self.wiki_course_root, base_page)

    def test_count_pages(self):
        from fun.utils import funwiki
        count = funwiki.count_articles(self.course)
        self.assertEqual(6, count)

    def test_get_page_tree(self):
        # [<URLPath: RUN/>, [<URLPath: RUN/page1/>, [<URLPath: RUN/page1/page11/>, [<URLPath: RUN/page1/page11/page111/>, <URLPath: RUN/page1/page11/page112/>]], <URLPath: RUN/page2/>]]
        from fun.utils import funwiki
        base_page = funwiki.get_base_page(self.course)
        tree = funwiki.get_page_tree([base_page])
        self.assertEqual(2, len(tree))  # root page and list of its children
        self.assertEqual(3, len(tree[1]))  # page1, page2 and list of page1's children
        self.assertEqual(2, len(tree[1][1]))  # page11, and list of it's 2 children

    def test_render_html_tree(self):
        from fun.utils import funwiki
        base_page = funwiki.get_base_page(self.course)
        tree = funwiki.get_page_tree([base_page])
        tree, html = funwiki.render_html_tree(tree, '')
        self.assertEqual(2, len(BeautifulSoup(html).find('ul').find('ul').find('ul').find_all('li')))  # page111 and page112
