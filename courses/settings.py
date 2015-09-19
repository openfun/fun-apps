from django.conf import settings


# Cutoff number of days to consider that a course starts soon or ends soon.
NUMBER_DAYS_TOO_LATE = getattr(settings, 'NUMBER_DAYS_TOO_LATE', 7)
