# -*- coding: utf-8 -*-

import datetime

from django.conf import settings

from haystack import indexes
from haystack.backends import elasticsearch_backend

from .models import Course
from newsfeed.models import Article


class ConfigurableElasticBackend(elasticsearch_backend.ElasticsearchSearchBackend):

    DEFAULT_ANALYZER = "custom_french_analyzer"

    def __init__(self, connection_alias, **kwargs):
        import ipdb; ipdb.set_trace()
        super(ConfigurableElasticBackend, self).__init__(connection_alias, **kwargs)
        user_settings = getattr(settings, 'ELASTICSEARCH_INDEX_SETTINGS')
        if user_settings:
            setattr(self, 'DEFAULT_SETTINGS', user_settings)

    def build_schema(self, fields):
        content_field_name, mapping = super(ConfigurableElasticBackend, self).build_schema(fields)

        for field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if not hasattr(field_class, 'facet_for') and not \
                                  field_class.field_type in('ngram', 'edge_ngram'):
                    field_mapping['analyzer'] = getattr(field_class, 'analyzer',
                                                            self.DEFAULT_ANALYZER)
            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)



class ConfigurableElasticSearchEngine(elasticsearch_backend.ElasticsearchSearchEngine):
    backend = ConfigurableElasticBackend


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


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    title = indexes.CharField(model_attr='title')
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()