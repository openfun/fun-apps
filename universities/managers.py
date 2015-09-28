from django.db import models


class UniversityManager(models.Manager):

    def with_related(self):
        queryset = self.prefetch_related('courses')
        queryset = queryset.annotate(courses_count=models.Count('courses'))
        return queryset

    def by_score(self):
        return self.with_related().order_by('-score', 'name')

    def by_name(self):
        return self.with_related().order_by('name')

    def have_page(self):
        return self.filter(detail_page_enabled=True)
