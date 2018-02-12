# -*- coding: utf-8 -*-
from django.db import models


class UniversityQuerySet(models.query.QuerySet):

    def not_obsolete(self):
        return self.filter(is_obsolete=False)

    def detail_page_enabled(self):
        return self.filter(detail_page_enabled=True)

    def with_related(self):
        queryset = self.prefetch_related('courses')
        return queryset

    def by_score(self):
        return self.order_by('-score', 'name')

    def featured(self, limit_to=None):
        """Featured universities have a detail page and are not obsolete"""
        qs = self.not_obsolete().detail_page_enabled().with_related().by_score()
        if limit_to is not None:
            qs = qs[:limit_to]
        return qs
