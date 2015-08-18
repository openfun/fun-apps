from django.db import models


class CourseSubjectManager(models.Manager):

    def featured(self):
        return self.filter(featured=True)

    def random_featured(self):
        return self.featured().order_by('?')
