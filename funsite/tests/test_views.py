import random

from django.core.urlresolvers import reverse
from django.test import TestCase

from student.models import CourseEnrollment
from student.tests.factories import UserFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from backoffice.tests.test_microsites import FAKE_MICROSITE1, FAKE_MICROSITE2
from fun.tests.utils import skipUnlessLms, setMicrositeTestSettings
import newsfeed.tests.factories as newsfactories


@skipUnlessLms
class TestHomepage(TestCase):

    def setUp(self):
        random.seed(0)

    def get_root_page(self):
        return self.client.get(reverse("root"))

    def test_no_course(self):
        self.get_root_page()

    def test_with_news(self):
        category = newsfactories.ArticleCategoryFactory.create()
        newsfactories.ArticleFactory.create(category=category)
        newsfactories.ArticleFactory.create(category=category)
        newsfactories.ArticleFactory.create(category=category)

        self.get_root_page()

    def test_unpublished_news_are_not_displayed(self):
        article = newsfactories.ArticleFactory.create(published=False)
        response = self.get_root_page()
        self.assertFalse(unicode(article.title) in response.content.decode("utf8"))

    @setMicrositeTestSettings(FAKE_MICROSITE2)
    def test_news_from_different_microsite_are_not_displayed(self):
        article = newsfactories.ArticleFactory.create(
            microsite=FAKE_MICROSITE1["SITE_NAME"],
            published=True
        )
        response = self.get_root_page()
        self.assertFalse(unicode(article.title) in response.content.decode("utf8"))


class TestLoginPage(ModuleStoreTestCase):

    def login_with_enrollment(self):
        course = CourseFactory.create()
        user = UserFactory.create()
        self.assertFalse(CourseEnrollment.is_enrolled(user, course.id))
        post_params = {
            'email': user.email,
            'password': 'test',
            'enrollment_action': 'enroll',
            'course_id': unicode(course.id)
        }
        self.client.post(reverse('login'), post_params)
        self.assertTrue(CourseEnrollment.is_enrolled(user, course.id))


@skipUnlessLms
class TestSearchProvider(TestCase):

    def test_render(self):
        response = self.client.get(reverse('searchprovider.xml'))
        self.assertEqual('text/xml', response.get('Content-Type'))
