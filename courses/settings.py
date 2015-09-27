from django.conf import settings


# Cutoff number of days to consider that a course starts soon or ends soon.
NUMBER_DAYS_TOO_LATE = getattr(settings, 'NUMBER_DAYS_TOO_LATE', 7)


THUMBNAIL_OPTIONS = getattr(settings, 'THUMBNAIL_OPTIONS', {
        'crop': True,
    })

THUMBNAIL_POSSIBLE_SIZES = (
    (270, 150),
    (150, 100),
    (100, 50),
)
