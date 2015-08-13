from django.db import models


class CourseSubjectManager(models.Manager):

    def random_featured(self):
        return self.filter(featured=True).order_by('?')
