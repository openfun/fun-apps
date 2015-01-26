from collections import defaultdict
from datetime import datetime

from django.db import connection
from django.db.models import Count

from opaque_keys.edx.keys import CourseKey
from opaque_keys import InvalidKeyError

import lms.lib.comment_client as comment_client
from student.models import CourseEnrollment


def enrollments_per_day(course_key_string, since=None):
    return enrollments_per(course_key_string, "day", since=since)

def enrollments_per_month(course_key_string, since=None):
    return enrollments_per(course_key_string, "month", since=since)

def enrollments_per(course_key_string, period_name, since=None):
    """
    Returns:
        [(date, count)] list
    """
    course_key = CourseKey.from_string(course_key_string)
    # Be careful: the following datr_trunc_sql does not produce the same result
    # with sqlite and postgresql, hence unit test discrepancies.
    #   sqlite: the day field is a string
    #   postgresql: the day field is a datetime object
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


def population_by_country(course_key_string):
    """Get geographical stats for a given course.

    Arguments:
        course_key_string (str): will be parsed to produce a CourseKey.

    Returns:
        course_population (dict): a dictionary of country codes (str) and
        student count (int) for active students associated to the course. If
        the course does not exist, return None.
    """
    try:
        course_key = CourseKey.from_string(course_key_string)
    except InvalidKeyError:
        return None
    country_field = "user__profile__country"
    query = (
        active_enrollments(course_key)
        .values(country_field)
        .annotate(population=Count(country_field))
        .order_by(country_field)
    )
    course_population = {}
    for result in query:
        country = result[country_field]
        course_population[country] = result["population"]
    return course_population

def active_enrollments(course_key):
    return (
        CourseEnrollment.objects
        .filter(course_id=course_key)
        .filter(user__is_active=True)
    )

def forum_threads(course_id):
    # TODO this is absolutely disgusting, untested code
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
        num_pages = result[2]
        if page == num_pages:
            break
        page += 1
    return threads

def forum_threads_per_day(threads):
    threads_per_day = defaultdict(int)
    for thread in threads:
        date = datetime.strptime(thread["created_at"], '%Y-%m-%dT%H:%M:%SZ')
        threads_per_day[datetime(year=date.year, month=date.month, day=1)] += 1
    return sorted(threads_per_day.items())

def most_active_username(threads):
    user_activity = defaultdict(int)
    for thread in threads:
        user_activity[thread["username"]] += 1
    best_username = None
    max_thread_count = 0
    for username, thread_count in user_activity.iteritems():
        if thread_count > max_thread_count:
            max_thread_count = thread_count
        best_username = username
    return best_username
