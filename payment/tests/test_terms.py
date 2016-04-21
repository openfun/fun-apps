# -*- coding: utf-8 -*-

from django.test import TestCase

from student.tests.factories import UserFactory

from ..models import TermsAndConditions, UserAcceptance


class TermsAndConditionTest(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.terms1v10 = TermsAndConditions.objects.create(name='test1', version='1.0',
                text=u"https://xkcd.com/501/")
        self.terms1v11 = TermsAndConditions.objects.create(name='test1', version='1.1',
                text=self.terms1v10.text)

        self.terms2v10 = TermsAndConditions.objects.create(name='test2', version='1.0',
                text=self.terms1v10.text)

    def test_get_latest(self):
        terms = TermsAndConditions.get_latest(name='test1')
        self.assertEqual('1.1', terms.version)

    def test_user_never_accepted(self):
        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='test1', user=self.user)
        self.assertEqual(self.terms1v11, terms)

        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='test2', user=self.user)
        self.assertEqual(self.terms2v10, terms)

        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='non-existent', user=self.user)
        self.assertEqual(False, terms)

    def test_user_accept_terms(self):
        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='test1', user=self.user)
        result = terms.accept(user=self.user)
        self.assertEqual(True, result)
        result = terms.accept(user=self.user)
        self.assertEqual(False, result)  # already accepted this version

        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='test1', user=self.user)
        self.assertEqual(False, result)  # already accepted latest

    def test_user_has_already_acccepted(self):
        UserAcceptance.objects.create(user=self.user, terms=self.terms1v11)
        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='test1', user=self.user)
        self.assertEqual(False, terms)


    def test_version_zero(self):
        """if a terms has a version 0 we want to considere it as automaticaly accepted."""
        TermsAndConditions.objects.create(name='test3', version='0',
                text=u"https://xkcd.com/501/")
        terms = TermsAndConditions.user_has_to_accept_new_version(
                name='test3', user=self.user)
        self.assertEqual(False, terms)
