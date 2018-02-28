# -*- coding: utf-8 -*-

from rest_framework import serializers

from courses.models import Course, CourseSubject
from fun_api import serializers as fun_serializers
from universities.serializers import UniversitySerializer, UniversityStaffSerializer


class CourseSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseSubject
        fields = ('description', 'featured', 'id', 'image', 'name', 'score', 'short_name')
        # All fields are readonly except "score"
        readonly_fields = ('description', 'featured', 'id', 'image', 'name', 'short_name')


class JSONSerializerField(serializers.Field):
    """
    Serializer for JSONField -- required to make field writable
    """
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class CourseSerializer(serializers.ModelSerializer):
    university_serializer_class = UniversitySerializer
    universities = UniversitySerializer(many=True)
    main_university = serializers.SerializerMethodField()
    subjects = CourseSubjectSerializer(many=True)
    thumbnails = JSONSerializerField(source='thumbnails_info')

    class Meta:
        model = Course
        fields = (
            'course_ended',
            'course_started',
            'end_date',
            'end_date_display',
            'enrollment_end_date',
            'enrollment_end_date_display',
            'enrollment_ended',
            'enrollment_start_date',
            'has_verified_course_mode',
            'id',
            'image_url',
            'key',
            'language',
            'level',
            'main_university',
            'session_display',
            'session_number',
            'short_description',
            'start_date',
            'start_date_display',
            'subjects',
            'thumbnails',
            'title',
            'universities',
            'university_name',
        )

    def get_main_university(self, obj):
        '''
        The main university is just the first one, when ordered
        using the order field.
        '''
        main_university = obj.get_first_university()
        if not main_university:
            return None
        return self.university_serializer_class(instance=main_university).data

    def get_has_verified_course_mode(self, obj):
        return obj.has_verified_course_mode


class PrivateCourseSerializer(CourseSerializer):
    """
    Presents data accessible to authenticated admin users.
    """
    university_serializer_class = UniversityStaffSerializer
    main_university = serializers.SerializerMethodField()
    universities = UniversityStaffSerializer(many=True)
    subjects = CourseSubjectSerializer(many=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('score', 'prevent_auto_update')


class CourseUpdateSerializer(fun_serializers.UpdateSerializerMixin, serializers.ModelSerializer):
    score = serializers.IntegerField(required=False)

    class Meta:
        model = Course
        fields = ('score',)
