from django.db import models


class CourseSubjectManager(models.Manager):

    def with_related(self):
        return self.prefetch_related('courses')

    def by_score(self):
        return self.with_related().order_by('-score')

    def by_name(self):
        return self.with_related().order_by('name')

    def featured(self):
        return self.filter(featured=True, image__isnull=False)

    def random_featured(self):
        return self.featured().order_by('?')
