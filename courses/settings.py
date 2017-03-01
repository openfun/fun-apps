from django.conf import settings


# Cutoff number of days to consider that a course starts soon or ends soon.
NUMBER_DAYS_TOO_LATE = getattr(settings, 'NUMBER_DAYS_TOO_LATE', 7)

FUN_THUMBNAIL_OPTIONS = getattr(settings, 'FUN_THUMBNAIL_OPTIONS', {
    'avatar': {'size': (270, 150), 'crop': True},
    'small': {'size': (150, 100), 'crop': 'smart'},
    'mini': {'size': (50, 50), 'crop': 'smart'},
})

COURSE_ADMIN_READ_ONLY_FIELDS = getattr(settings, 'COURSE_ADMIN_READ_ONLY_FIELDS',
    ('key', 'title', 'image_url', 'university_display_name', 'show_in_catalog',
    'show_about_page', 'start_date', 'end_date', 'enrollment_start_date',
    'enrollment_end_date', 'thumbnails_info')
)
