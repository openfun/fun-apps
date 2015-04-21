# -*- coding: utf-8 -*-

import datetime
import factory

from newsfeed import models


class ArticleFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.Article

    title = u"An awesome piece of news"
    slug = factory.Sequence(lambda n: 'a-great-slug-{0}'.format(n))
    text = u"J'étais un texte accentué !"
    created_at = factory.lazy_attribute(lambda x: datetime.datetime.now())


class FeaturedSectionFactory(factory.DjangoModelFactory):
    FACTORY_FOR = models.FeaturedSection

    title = u"Featured section from outer space"
    image = factory.django.ImageField()
