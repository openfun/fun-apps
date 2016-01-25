import datetime
from haystack import indexes
from .models import Course


class CourseIndex(indexes.SearchIndex, indexes.Indexable):
    key = indexes.CharField(model_attr='key')
    title = indexes.CharField(model_attr='title')
    key = indexes.CharField(model_attr='key')
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Course

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()