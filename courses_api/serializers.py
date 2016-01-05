# -*- coding: utf-8 -*-

from rest_framework import serializers

from courses.models import Course, CourseSubject
from universities.serializers import UniversitySerializer, PrivateUniversitySerializer


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


class CourseSerializer(serializers.ModelSerializer):
    universities = UniversitySerializer()
    subjects = CourseSubjectSerializer()
    session_display = serializers.CharField(source='session_display')
    thumbnails = serializers.CharField(source='thumbnails_info')
    start_date_display = serializers.CharField(source='start_date_display')
    enrollment_ended = serializers.BooleanField(source='enrollment_ended')
    end_date_display = serializers.CharField(source='end_date_display')
    course_ended = serializers.BooleanField(source='course_ended')
    course_started = serializers.BooleanField(source='course_started')
    university_name = serializers.CharField(source='university_name')

    class Meta:
        model = Course
        fields = (
            'id',
            'key',
            'universities',
            'university_name',
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
            'course_started',
            'course_ended',
            'enrollment_ended',
            'session_number',
            'session_display',
            'thumbnails',
        )


class PrivateCourseSerializer(CourseSerializer):
    '''
    Presents data accessible to authenticated admin users.
    '''

    universities = PrivateUniversitySerializer()
    subjects = PrivateCourseSubjectSerializer()

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ('score',)


class CourseUpdateSerializer(serializers.ModelSerializer):
    score = serializers.IntegerField(required=False)

    class Meta:
        model = Course
        fields = ('score',)
