from StringIO import StringIO

from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from xmodule.modulestore.tests.factories import CourseFactory

from fun.tests.utils import skipUnlessLms


@skipUnlessLms
class TestRemoveWikiWritePermissions(ModuleStoreTestCase):

    def setUp(self):
        super(TestRemoveWikiWritePermissions, self).setUp()
        from course_wiki.views import get_or_create_root
        self.wiki_root = get_or_create_root()
        self.course = CourseFactory.create(org='ORG', display_name='COURSE', number='RUN')

    def reload_article(self, article):
        from wiki.models.article import Article
        return Article.objects.get(pk=article.pk)

    def create_article(self, parent, slug, title):
        from wiki.models.urlpath import URLPath
        return URLPath.create_article(parent, slug, title=title, article_kwargs={
            'group_write': True,
            'other_write': True,
        })

    def remove_write_permissions(self):
        from fun.management.commands import remove_wiki_write_permissions
        command = remove_wiki_write_permissions.Command()
        command.execute(unicode(self.course.id), stdout=StringIO())

    def assertHasWritePermission(self, article):
        article = self.reload_article(article)
        self.assertTrue(article.group_write)
        self.assertTrue(article.other_write)

    def assertHasNoWritePermission(self, article):
        article = self.reload_article(article)
        self.assertFalse(article.group_write)
        self.assertFalse(article.other_write)

    def test_remove_permissions(self):
        # Create parent/child articles
        wiki_course_root = self.create_article(self.wiki_root, self.course.wiki_slug, "Root article")
        wiki_course_child = self.create_article(wiki_course_root, 'child-article', "Child article")

        self.assertHasWritePermission(wiki_course_root)
        self.assertHasWritePermission(wiki_course_child)
        self.remove_write_permissions()
        self.assertHasNoWritePermission(wiki_course_root)
        self.assertHasNoWritePermission(wiki_course_child)

    def test_remove_permissions_from_multiple_articles_with_same_slug(self):
        # Create parent/child articles with identical slugs
        wiki_course_root = self.create_article(self.wiki_root, self.course.wiki_slug, "Root article")
        wiki_course_child_1 = self.create_article(wiki_course_root, self.course.wiki_slug, "Child article 1")
        wiki_course_child_2 = self.create_article(wiki_course_root, 'child-article', "Child article")

        self.remove_write_permissions()
        self.assertHasNoWritePermission(wiki_course_root)
        self.assertHasNoWritePermission(wiki_course_child_1)
        self.assertHasNoWritePermission(wiki_course_child_2)
