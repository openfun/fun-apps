# -*- coding: utf-8 -*-

import factory
from factory import fuzzy

from ..choices import UNIVERSITY_PARTNERSHIP_LEVEL
from ..models import University


class UniversityFactory(factory.DjangoModelFactory):
    name = fuzzy.FuzzyText(length=255)
    short_name = fuzzy.FuzzyText(length=100)
    code = factory.Sequence("university{0}".format)
    certificate_logo = factory.django.ImageField(color='blue')
    logo = factory.django.ImageField(color='white')
    detail_page_enabled = factory.fuzzy.FuzzyChoice((True, False))
    is_obsolete = factory.fuzzy.FuzzyChoice((True, False))
    slug = factory.Sequence("university{0}".format)
    banner = factory.django.ImageField(color='red')
    description = fuzzy.FuzzyText(length=1000)
    partnership_level = factory.fuzzy.FuzzyChoice(
        tuple(l[0] for l in UNIVERSITY_PARTNERSHIP_LEVEL))
    score = factory.fuzzy.FuzzyInteger(low=0, high=999)
    prevent_auto_update = factory.fuzzy.FuzzyChoice((True, False))

    class Meta(object):
        model = University
