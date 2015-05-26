# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class WikiTestCase(ModuleStoreTestCase):
    def create_urlpath(self, parent, slug):
        """Creates an article at /parent/slug and returns its URLPath"""
        from wiki.models import URLPath
        return URLPath.create_article(parent=parent, slug=slug, title=slug, article_kwargs={'owner': self.user})

    def setUp(self):
        super(WikiTestCase, self).setUp(create_user=True)


    def test_get_activity(self):
        from course_wiki.views import get_or_create_root
        from course_wiki.utils import course_wiki_slug

        course = CourseFactory.create()
        wiki = get_or_create_root()

        wiki_page = self.create_urlpath(wiki, course_wiki_slug(course))
        wiki_page2 = self.create_urlpath(wiki_page, 'Child')
        _wiki_page3 = self.create_urlpath(wiki_page2, 'Grandchild')

        instructor = InstructorFactory.create(course_key=course.id)
        self.client.login(username=instructor.username, password="test")

        # TODO we should probably test something more here
        response = self.client.get(reverse('course-dashboard:wiki-activity',
                kwargs={'course_id': course.id.to_deprecated_string()}))
        self.assertEqual(200, response.status_code)
