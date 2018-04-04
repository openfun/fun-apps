# _*_ coding: utf8 _*_
"""
Test suite for our customization of django-masquerade's middleware that allows
disabling masquerade on some url patterns.
"""

from django.test import TestCase
from django.test.client import RequestFactory

from student.tests.factories import UserFactory

from ..middleware import PathLimitedMasqueradeMiddleware as Middleware


class PathExcludeMasqueradeMiddlewareTestCase(TestCase):
    """
    Test Case unit testing our overrides to django-masquerade's middleware.
    """
    def test_masquerade_is_effective_on_lms_pages(self):
        """
        Masquerade should be effective on lms pages.
        The url patterns in the middleware are hardcoded, so the test must also hardcode the
        paths it is testing so that the test breaks if the path in changed in urls.py.
        """
        factory = RequestFactory()
        staff_user = UserFactory(is_staff=True)
        target_user = UserFactory()
        for uri in ['/', '/account/settings']:
            request = factory.get(uri)
            request.user = staff_user
            request.session = {'mask_user': target_user.username}
            Middleware().process_request(request)

            self.assertTrue(request.user.is_masked)
            self.assertEqual(request.user, target_user)
            self.assertEqual(request.user.original_user, staff_user)

    def test_masquerade_is_disabled_on_admin_and_backoffice_pages(self):
        """
        Masquerade should be disabled on admin and backoffice pages.
        The url patterns in the middleware are hardcoded, so the test must also hardcode the
        paths it is testing so that the test breaks if the path in changed in urls.py.
        """
        factory = RequestFactory()
        staff_user = UserFactory(is_staff=True)
        target_user = UserFactory()
        for uri in ['/admin/courses/course', 'backoffice/users']:
            request = factory.get(uri)
            request.user = staff_user
            request.session = {'mask_user': target_user.id}
            Middleware().process_request(request)

            self.assertFalse(request.user.is_masked)
            self.assertEqual(request.user, staff_user)
            self.assertTrue(request.user.original_user is None)
