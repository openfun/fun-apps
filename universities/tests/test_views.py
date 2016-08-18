from django.test import TestCase

from universities.tests.factories import UniversityFactory
from universities import models
from universities import views


class UniversityQuerysetsTests(TestCase):

    def test_landing_view(self):
        u1 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=False)
        u2 = UniversityFactory.create(detail_page_enabled=False, is_obsolete=False)
        u3 = UniversityFactory.create(detail_page_enabled=False, is_obsolete=True)
        u4 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=True)

        listed_universities = list(views.UniversityLandingView().get_queryset())

        self.assertTrue(u1 in listed_universities)
        self.assertFalse(u2 in listed_universities)
        self.assertFalse(u3 in listed_universities)
        self.assertFalse(u4 in listed_universities)

    def test_featured(self):
        u1 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=False, score=1)
        u2 = UniversityFactory.create(detail_page_enabled=False, is_obsolete=False, score=2)
        u3 = UniversityFactory.create(detail_page_enabled=False, is_obsolete=True, score=3)
        u4 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=True, score=4)

        featured_universities = list(models.University.objects.featured(4))

        self.assertTrue(u1 in featured_universities)
        self.assertFalse(u2 in featured_universities)
        self.assertFalse(u3 in featured_universities)
        self.assertFalse(u4 in featured_universities)
        self.assertEqual(1, len(featured_universities))

    def test_non_obsolete(self):
        u1 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=False)
        u2 = UniversityFactory.create(detail_page_enabled=True, is_obsolete=True)

        non_obsolete = models.University.objects.non_obsolete()
        self.assertIn(u1, non_obsolete)
        self.assertNotIn(u2, non_obsolete)