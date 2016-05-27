# -*- coding: utf-8 -*-

import csv
from collections import defaultdict
from datetime import datetime
from StringIO import StringIO
import time

from django.http import HttpResponse
from django.shortcuts import render
from django.utils.formats import date_format

from wiki.models import URLPath, Article

from course_wiki.utils import course_wiki_slug
from courseware.courses import get_course_by_id
from opaque_keys.edx.keys import CourseKey
from util.views import ensure_valid_course_key

from fun.utils.views import staff_required, staff_required_or_level
from fun.utils.countries import get_country_name

from . import stats


@ensure_valid_course_key
@staff_required_or_level('staff')
def enrollment_stats(request, course_id):
    enrollments = stats.EnrollmentStats(course_id)
    return enrollment_stats_response(request, enrollments, 'course_dashboard/enrollment-stats.html')

@staff_required
def global_enrollment_stats(request):
    enrollments = stats.EnrollmentStats(None)
    return enrollment_stats_response(request, enrollments, 'course_dashboard/enrollment-stats-global.html')

def enrollment_stats_response(request, enrollments, template):
    if request.GET.get("format") == "csv":
        return csv_response(["date", "enrollments"], enrollments.per_date, "enrollments.csv")
    context = enrollment_stats_context(enrollments)
    return render(request, template, context)

def enrollment_stats_context(enrollments):
    enrollments_per_day, enrollments_per_timestamp = formatted_dates(enrollments.per_date)
    best_day = None
    if enrollments_per_day:
        best_day = max(enrollments_per_day, key=lambda e: e[1])

    return {
        "active_tab": "enrollment_stats",
        "course_id": enrollments.course_id,
        "enrollments_per_day": enrollments_per_day,
        "enrollments_per_timestamp": enrollments_per_timestamp,
        "average_enrollments_per_day": enrollments.daily_average(),
        "best_day": best_day,
        "total_population": enrollments.total(),
        "day_span": enrollments.day_span(),
    }

@ensure_valid_course_key
@staff_required_or_level('staff')
def student_map(request, course_id):
    course_population_by_country_code = stats.population_by_country(course_id)
    return student_map_response(request, course_population_by_country_code,
                                'course_dashboard/student-map.html', course_id)

@staff_required
def global_student_map(request):
    course_population_by_country_code = stats.population_by_country(None)
    return student_map_response(request, course_population_by_country_code,
                                'course_dashboard/student-map-global.html', None)

def student_map_response(request, course_population_by_country_code, template, course_id):
    top_countries = sorted(
        [(population, code, get_country_name(code))
         for code, population in course_population_by_country_code.iteritems()],
        reverse=True
    )
    if request.GET.get("format") == "csv":
        data_rows = [(country, population) for population, _code, country in top_countries]
        return csv_response(["country", "enrollments"], data_rows, "countries.csv")
    total_population = sum(course_population_by_country_code.values())

    return render(request, template, {
        "active_tab": "student_map",
        "course_id": course_id,
        "course_population": course_population_by_country_code,
        "top_countries": top_countries,
        "total_population": total_population,
    })

@ensure_valid_course_key
@staff_required_or_level('staff')
def forum_activity(request, course_id):
    threads = stats.forum_threads(course_id)
    threads_per_date = stats.forum_threads_per_day(threads)
    if request.GET.get("format") == "csv":
        return csv_response(["date", "threads"], threads_per_date, "forum-activity.csv")

    threads_per_day, threads_per_timestamp = formatted_dates(threads_per_date)
    total_threads = len(threads)
    most_active_thread = None
    least_active_thread = None
    most_active_user = stats.most_active_user(threads)
    if threads:
        most_active_thread = max(threads, key=lambda t: t["comments_count"])
        least_active_thread = min(threads, key=lambda t: t["comments_count"])

    return render(request, 'course_dashboard/forum-activity.html', {
        "active_tab": "forum_activity",
        "course_id": course_id,
        "threads_per_day": threads_per_day,
        "threads_per_timestamp": threads_per_timestamp,
        "most_active_thread": most_active_thread,
        "least_active_thread": least_active_thread,
        "total_threads": total_threads,
        "most_active_user": most_active_user,
    })

def get_urlpath(course_id):
    """Returns url path of root wiki page for course."""
    # Offical edX way to replace slashes by dots: course_key.replace('/', '.')
    course_key = CourseKey.from_string(course_id)
    course = get_course_by_id(course_key)
    course_slug = course_wiki_slug(course)
    try:
        urlpath = URLPath.get_by_path(course_slug)
    except URLPath.DoesNotExist:
        urlpath = None
    return urlpath


@ensure_valid_course_key
@staff_required_or_level('staff')
def wiki_activity(request, course_id):

    urlpath = get_urlpath(course_id)
    data = {}
    data['article_creation'] = defaultdict(int)
    data['revision_counts'] = defaultdict(int)
    data['article_revision'] = defaultdict(int)
    data['user_activity'] = defaultdict(int)
    data['urlpaths'] = []
    data['page_count'] = 0

    if urlpath:
        root = Article.objects.get(id=urlpath.id)  # get the root article of the course
        urlpaths = root.descendant_objects()
        for urlpath in urlpaths:
            data['urlpaths'].append(urlpath)
            data['article_creation'][urlpath.article.created.date()] += 1
            for revision in urlpath.article.articlerevision_set.all():
                data['revision_counts'][urlpath] += 1
                data['article_revision'][revision.created.date()] += 1
                # use Article owner if revision is anonymous (tests)
                data['user_activity'][revision.user or urlpath.article.owner] += 1

    series = []
    series.append(sorted(formatted_dates(data['article_creation'].items())[1], key=lambda item: item[0]))
    series.append(sorted(formatted_dates(data['article_revision'].items())[1], key=lambda item: item[0]))

    most_active_pages = sorted(
        data['revision_counts'].items(), key=lambda item: item[1], reverse=True)
    last_created = sorted(data['urlpaths'], key=lambda item: item.article.created, reverse=True)
    most_active_users = sorted(data['user_activity'].items(), key=lambda item: item[1], reverse=True)

    return render(request, 'course_dashboard/wiki-activity.html', {
        "series": series,
        "most_active_pages": most_active_pages,
        "last_created": last_created,
        "most_active_users": most_active_users,
        "page_count": len(data['urlpaths']),
        "user_count": len(data['user_activity'].items()),
        "revision_count": sum(data['article_revision'].values()),
        "active_tab": "wiki_activity",
        "course_id": course_id,
    })

def csv_response(header_row, data_rows, filename):
    def encode_data(data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, datetime):
            return data.strftime('%Y/%m/%d')
        else:
            return u"{}".format(data)

    response_content = StringIO()
    writer = csv.writer(response_content)
    writer.writerow([field.encode('utf-8') for field in header_row])
    for data_row in data_rows:
        writer.writerow([encode_data(d) for d in data_row])
    response_content.seek(0)

    response = HttpResponse(response_content.read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response

def formatted_dates(date_list):
    """Formats a (date, value) list for usage in a template.

    Arguments:
    date_list ((datetime, value) list)

    Returns:
        (str, value) list
        [int, value] list
    """
    stats_per_day = [
        (date_format(date), count) for date, count in date_list
    ]
    stats_per_timestamp = [
        [date_to_js_timestamp(date), count] for date, count in date_list
    ]
    return stats_per_day, stats_per_timestamp

def date_to_js_timestamp(date):
    """Convert a date to a javascript timestamp.

    Arguments:
        date (datetime)

    Returns:
        timestamp (int): the timestamp is for js usage, i.e: it is 1000x the
        python timestamp.
    """
    return time.mktime(date.timetuple())*1000

@ensure_valid_course_key
@staff_required_or_level('staff')
def certificate_stats(request, course_id):
    """Return basic certificate stats (success, failure)."""
    certif_stats = stats.CertificateStats(course_id)
    return render(request, 'course_dashboard/certificate-stats.html',
                  {'course_id': course_id,
                   'passing': certif_stats.passing(),
                   'not_passing': certif_stats.not_passing(),
                   'total':certif_stats.total()})
