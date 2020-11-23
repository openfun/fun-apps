# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.test import TestCase

from student.tests.factories import UserFactory

from fun.tests.utils import skipUnlessLms, skipUnlessCms

from ..models import TermsAndConditions, UserAcceptance, PAYMENT_TERMS

from factories import TermsAndConditionsFactory, TranslatedTermsFactory


@skipUnlessLms
class TermsAndConditionTest(TestCase):
    def setUp(self):
        """
        Create 2 kinds of terms and condition, one in 2 versions
        """
        self.user = UserFactory()
        self.terms1v10 = TermsAndConditionsFactory(
            name="test1", version="1.0", text=u"https://xkcd.com/501/"
        )
        self.terms1v11 = TermsAndConditionsFactory(
            name="test1", version="1.1", text=self.terms1v10.text
        )
        self.terms2v10 = TermsAndConditionsFactory(
            name="test2", version="1.0", text=self.terms1v10.text
        )

    def test_get_latest(self):
        """
        Latest version of `test1` should be 1.1
        """
        terms = TermsAndConditions.get_latest(name="test1")
        self.assertEqual("1.1", terms.version)

    def test_user_never_accepted(self):
        """
        Rest what version of terms earch user should be asked to accept.
        """
        # User should have to accept the newer one of `test1`
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="test1", user=self.user
        )
        self.assertEqual(self.terms1v11, terms)

        # User should have to accept the only one of `test2`
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="test2", user=self.user
        )
        self.assertEqual(self.terms2v10, terms)

        # User do not have to accept a non existent terms
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="non-existent", user=self.user
        )
        self.assertEqual(False, terms)

    def test_user_accept_terms(self):
        """
        Test that user who alrady accepted terms do not need to do it again
        """
        # User has to accept latest of `test1`
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="test1", user=self.user
        )
        # OK then
        result = terms.accept(user=self.user)
        self.assertEqual(True, result)
        # You can not accept 2 times
        result = terms.accept(user=self.user)
        self.assertEqual(False, result)  # already accepted this version

        # what version of `test1`does user have to accept ?
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="test1", user=self.user
        )
        self.assertEqual(False, result)  # already accepted latest

    def test_user_has_already_acccepted(self):
        """
        Test that user_has_to_accept_new_version returns False if user already accepted latest
        """
        UserAcceptance.objects.create(user=self.user, terms=self.terms1v11)
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="test1", user=self.user
        )
        self.assertEqual(False, terms)

    def test_version_zero(self):
        """
        If a terms has a version 0 we want to considere it as automaticaly accepted.
        """
        TermsAndConditions.objects.create(
            name="test3", version="0", text=u"https://xkcd.com/501/"
        )
        terms = TermsAndConditions.user_has_to_accept_new_version(
            name="test3", user=self.user
        )
        self.assertEqual(False, terms)


class TermsAndConditionViewsTest(TestCase):
    """
    Create FUN terms and condition, and validate user forced acceptance
    """

    def setUp(self):
        self.user = UserFactory()
        self.terms1v10 = TermsAndConditionsFactory(
            name=PAYMENT_TERMS, version="1.0", text=u"https://xkcd.com/501/"
        )

    @skipUnlessLms
    def test_forced_acceptation(self):
        """
        User should be redirected to terms page until he accepted
        """
        self.client.login(username=self.user.username, password="test")
        # attempt to acces dashboard when still having to accept terms
        response = self.client.get(reverse("dashboard"))
        # should be redirected to acceptance page
        self.assertRedirects(response, reverse("payment:terms-page"))
        # accept then
        response = self.client.post(reverse("payment:accept-terms"))
        # and should be redirected to dashbord
        self.assertRedirects(response, reverse("dashboard"))

    @skipUnlessLms
    def test_forced_acceptation_with_next_param(self):
        """
        Once user accepted new terms and conditions, he/she should be redirected
        to the route provided in next param if it exists
        """
        self.client.login(username=self.user.username, password="test")
        # attempt to acces dashboard when still having to accept terms
        response = self.client.get(
            "/u/{username:s}".format(username=self.user.username)
        )
        # should be redirected to acceptance page
        self.assertRedirects(response, reverse("payment:terms-page"))
        # accept then
        response = self.client.post(reverse("payment:accept-terms"))
        # and should be redirected to dashbord
        self.assertRedirects(
            response, reverse("/u/{username:s}".format(username=self.user.username))
        )
