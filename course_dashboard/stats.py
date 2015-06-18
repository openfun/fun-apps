from collections import defaultdict
from datetime import datetime

from django.db import connection
from django.db.models import Count

from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

import lms.lib.comment_client as comment_client
from student.models import CourseEnrollment
from student.models import User

import fun.utils.countries


def enrollments_per_day(course_key_string=None, since=None):
    """
    Returns:
        [(date, count)] list sorted by increasing date.
    """
    course_key = CourseKey.from_string(course_key_string) if course_key_string else None
    # Be careful: the following datr_trunc_sql does not produce the same result
    # with sqlite and postgresql, hence unit test discrepancies.
    #   sqlite: the day field is a string
    #   postgresql: the day field is a datetime object
    period_name = 'day'
    truncate_date = connection.ops.date_trunc_sql(period_name, 'created')
    query = active_enrollments(course_key)
    if since is not None:
        query = query.filter(created__gte=since)
    query = (query
        .extra({period_name: truncate_date})
        .values(period_name)
        .annotate(enrollment_count=Count("pk"))
        .order_by(period_name)
    )
    def dateify(date):
        if isinstance(date, datetime):
            return date
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    return [(dateify(result[period_name]), result['enrollment_count']) for result in query]


def population_by_country(course_key_string=None):
    """Get geographical stats for a given course.

    Arguments:
        course_key_string (str): will be parsed to produce a CourseKey.

    Returns:
        course_population (dict): a dictionary of country codes (str) and
        student count (int) for active students associated to the course. If
        the course does not exist, return None.
    """
    if course_key_string is None:
        course_key = None
    else:
        try:
            course_key = CourseKey.from_string(course_key_string)
        except InvalidKeyError:
            return None
    country_field = "user__profile__country"
    query = (
        active_enrollments(course_key)
        .values(country_field)
        .annotate(population=Count(country_field))
        .filter(population__gt=0)
        .order_by(country_field)
    )
    course_population = defaultdict(int)
    for result in query:
        country = fun.utils.countries.territory_country(result[country_field])
        course_population[country] += result["population"]
    # Because there is no NULL country we need to perform an additional query
    # to include enrollments with NULL country.
    null_country_users = active_enrollments(course_key).filter(**{country_field + "__isnull": True}).count()
    if null_country_users > 0:
        course_population[fun.utils.countries.UNKNOWN_COUNTRY_CODE] += null_country_users
    return course_population

def active_enrollments(course_key=None):
    """
    Return a queryset of active course enrollments.
    """
    queryset = CourseEnrollment.objects.filter(is_active=True)
    if course_key is not None:
        queryset = queryset.filter(course_id=course_key)
    return queryset

def forum_threads(course_id):
    """
    Search for all forum threads created in the given course.

    Returns:

        An array of thread (dict) objects
    """
    # Note: this is untested code
    page = 1
    num_pages = 1
    threads = []
    while True:
        result = comment_client.Thread.search({
            "course_id": course_id,
            "page": page,
            "per_page": 200,
        })
        threads += result[0]
        # Iterate over all result pages
        num_pages = result[2]
        if page == num_pages:
            break
        page += 1
    return threads

def forum_threads_per_day(threads):
    """Count the number of forum threads created per day.

    Args:

        threads: array of dict objects, as returned by the forum API. In
        particular, each thread has a "created_at" key that points to a string
        date value.

    Returns:

         A sorted array of (date, count) pairs where date is a datetime object
         and count is an integer. Dates at which no forum entry was created are
         not listed.
    """
    threads_per_day = defaultdict(int)
    for thread in threads:
        date = datetime.strptime(thread["created_at"], '%Y-%m-%dT%H:%M:%SZ')
        threads_per_day[datetime(year=date.year, month=date.month, day=date.day)] += 1
    return sorted(threads_per_day.items())

def most_active_user(threads):
    if threads:
        username = most_active_username(threads)
        return User.objects.get(username=username)

def most_active_username(threads):
    user_activity = defaultdict(int)
    for thread in threads:
        user_activity[thread["username"]] += 1
    # user_activity is of the form {"username": count, ...}
    return max(user_activity.items(), key=lambda i: i[1])[0]

class EnrollmentStats(object):
    """Provide enrollments stats for a given course."""

    def __init__(self, course_id=None, since=None):
        self.course_id = course_id
        self.since = since
        self.per_date = enrollments_per_day(self.course_id, since=since)

    def day_span(self):
        """Number of days covered by the stats."""
        days = 1
        if self.per_date:
            days = (self.per_date[-1][0] - self.per_date[0][0]).days + 1
        return days

    def total(self):
        """Total number of enrollments"""
        return sum(e[1] for e in self.per_date)

    def daily_average(self):
        """Average enrollments per day"""
        return self.total() * 1. / self.day_span()
