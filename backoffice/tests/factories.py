# -*- coding: utf-8 -*-

import factory
from factory.django import DjangoModelFactory

from student.models import UserStanding, Registration, UserSignupSource
from student.tests.factories import UserFactory


class MicrositeUserFactory(DjangoModelFactory):
    FACTORY_FOR = UserSignupSource

    user = factory.SubFactory(UserFactory)

