# -*- coding: utf-8 -*-

import factory
from factory.django import DjangoModelFactory

from student.models import UserSignupSource
from student.tests.factories import UserFactory


class MicrositeUserFactory(DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta(object):
        model = UserSignupSource
