# -*- coding: utf-8 -*-

from rest_framework import serializers

from courses.models import Course, CourseSubject
from fun_api import serializers as fun_serializers
from universities_api.serializers import UniversitySerializer, PrivateUniversitySerializer


class CourseSubjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = CourseSubject
        fields = ('id', 'name')


class PrivateCourseSubjectSerializer(CourseSubjectSerializer):
    '''
    Presents data accessible to authenticated admin users.
    '''

    class Meta(CourseSubjectSerializer.Meta):
        fields = CourseSubjectSerializer.Meta.fields + ('score',)


class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
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
            'id',
            'key',
            'universities',
            'university_name',
            'main_university',
            'title',
            'short_description',
            'level',
            'subjects',
            'image_url',
            'start_date',
            'start_date_display',
            'end_date_display',
            'end_date',
            'enrollment_start_date',
            'enrollment_end_date',
            'enrollment_end_date_display',
            'course_started',
            'course_ended',
            'enrollment_ended',
            'session_number',
            'session_display',
            'thumbnails',
            'has_verified_course_mode',
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
    '''
    Presents data accessible to authenticated admin users.
    '''
    university_serializer_class = PrivateUniversitySerializer
    main_university = serializers.SerializerMethodField()
    universities = PrivateUniversitySerializer(many=True)
    subjects = PrivateCourseSubjectSerializer(many=True)

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('score', 'prevent_auto_update')


class CourseUpdateSerializer(fun_serializers.UpdateSerializerMixin, serializers.ModelSerializer):
    score = serializers.IntegerField(required=False)

    class Meta:
        model = Course
        fields = ('score',)
