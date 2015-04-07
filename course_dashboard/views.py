import csv
import time
from datetime import datetime
from StringIO import StringIO

from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.utils.formats import date_format
from django_countries import countries

from fun.utils.views import ensure_valid_course_key
from fun.utils.views import staff_required, staff_required_or_level
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
    worst_day = None
    if enrollments_per_day:
        best_day = max(enrollments_per_day, key=lambda e: e[1])
        worst_day = min(enrollments_per_day, key=lambda e: e[1])

    return {
        "active_tab": "enrollment_stats",
        "course_id": enrollments.course_id,
        "enrollments_per_day": enrollments_per_day,
        "enrollments_per_timestamp": enrollments_per_timestamp,
        "average_enrollments_per_day": enrollments.daily_average(),
        "best_day": best_day,
        "worst_day": worst_day,
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

def get_country_name(country_code):
    if country_code == '':
        return unicode(_("Unknown"))
    return unicode(countries.name(country_code))

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


def csv_response(header_row, data_rows, filename):
    def encode_data(data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, datetime):
            return data.strftime('%Y/%m/%d')
        else:
            return data

    response_content = StringIO()
    writer = csv.writer(response_content)
    writer.writerow(header_row)
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
