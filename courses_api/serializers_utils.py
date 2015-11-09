class CoursesCountSerializerMixin(object):

    def get_courses_count(self, obj):
        '''
        We are using this method to access the annotated count field.
        Because it's annotated, this field is not always available on
        the instance - that's why we retrieve it dynamically.
        Trying to retrieve the value as any other 'concrete' model
        attribute cause an issue with django rest framework.
        '''
        return getattr(obj, 'courses_count', None)
