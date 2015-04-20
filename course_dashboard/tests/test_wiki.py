# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test.utils import override_settings

from courseware.tests.factories import InstructorFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from course_wiki.utils import user_is_article_course_staff, course_wiki_slug
from course_wiki.views import get_or_create_root
from student.models import UserProfile
from wiki.models import URLPath


class WikiTestCase(ModuleStoreTestCase):
    def create_urlpath(self, parent, slug):
        """Creates an article at /parent/slug and returns its URLPath"""

        return URLPath.create_article(parent=parent, slug=slug, title=slug, article_kwargs={'owner': self.user})

    def setUp(self):
        super(WikiTestCase, self).setUp(create_user=True)


    def test(self):

        self.course = CourseFactory.create()
        self.wiki = get_or_create_root()

        wiki_page = self.create_urlpath(self.wiki, course_wiki_slug(self.course))
        wiki_page2 = self.create_urlpath(wiki_page, 'Child')
        wiki_page3 = self.create_urlpath(wiki_page2, 'Grandchild')

        instructor = InstructorFactory.create(course_key=self.course.id)
        self.client.login(username=instructor.username, password="test")

        response = self.client.get(reverse('course-dashboard:wiki-activity',
                kwargs={'course_id': self.course.id.to_deprecated_string()}))
        self.assertEqual(200, response.status_code)
