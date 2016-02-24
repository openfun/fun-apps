# -*- coding: utf-8 -*-
from django.db import models

from fun.utils.managers import ChainableManager


class UniversityQuerySet(models.query.QuerySet):

    def active(self):
        return self.filter(is_obsolete=False)

    def detail_page_enabled(self):
        return self.filter(detail_page_enabled=True)

    def with_related(self):
        queryset = self.prefetch_related('courses')
        return queryset

    def by_score(self):
        return self.order_by('-score', 'name')


class UniversityManager(ChainableManager):
    queryset_class = UniversityQuerySet

    def featured(self, limit_to=7):
        return self.active().with_related().by_score()[:limit_to]
