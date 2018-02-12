# -*- coding: utf-8 -*-

from django.conf import settings

from haystack import indexes
from haystack.backends import elasticsearch_backend

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from .models import Course


# pylint: disable=W0223
class ConfigurableElasticBackend(elasticsearch_backend.ElasticsearchSearchBackend):
    """
    Override Hastack default backend to use our own ES configuration as DEFAULT_SETTINGS
    constant is hardcoded .
    """

    DEFAULT_ANALYZER = "custom_french_analyzer"

    def __init__(self, connection_alias, **kwargs):
        super(ConfigurableElasticBackend, self).__init__(connection_alias, **kwargs)
        user_settings = getattr(settings, 'ELASTICSEARCH_INDEX_SETTINGS')
        if user_settings:
            self.DEFAULT_SETTINGS = user_settings

    def build_schema(self, fields):
        """
        This will affect DEFAULT_ANALYZER to all fields of type string if there are no other
        analyzer explicitly defined.
        """
        content_field_name, mapping = super(ConfigurableElasticBackend, self).build_schema(fields)
        for _field_name, field_class in fields.items():
            field_mapping = mapping[field_class.index_fieldname]

            if field_mapping['type'] == 'string' and field_class.indexed:
                if (
                        not hasattr(field_class, 'facet_for') and
                        field_class.field_type not in ('ngram', 'edge_ngram')):
                    field_mapping['analyzer'] = getattr(
                        field_class, 'analyzer', self.DEFAULT_ANALYZER)
            mapping.update({field_class.index_fieldname: field_mapping})
        return (content_field_name, mapping)


class ConfigurableElasticSearchEngine(elasticsearch_backend.ElasticsearchSearchEngine):
    backend = ConfigurableElasticBackend


class CourseIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Build the document containing information we want to index from
    Course model.
    """
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Course

    def index_queryset(self, using=None):
        return self.get_model().objects.public()

    def prepare(self, instance):
        """
        As course syllabus is store in Mongo we retrieve it and happend to
        document created from Course model fields in
        courses/templates/search/indexes/courses/course_text.txt
        """
        self.prepared_data = super(CourseIndex, self).prepare(instance)

        usage_key = CourseKey.from_string(instance.key).make_usage_key('about', 'overview')
        syllabus = modulestore().get_item(usage_key).data

        self.prepared_data['text'] += '\n' + syllabus
        return self.prepared_data

    def get_updated_field(self):
        return 'modification_date'
