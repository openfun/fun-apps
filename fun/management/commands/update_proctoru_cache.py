# -*- coding: utf-8 -*-
import datetime
import logging
import requests
from optparse import make_option

from course_modes.models import CourseMode

from django.core.management.base import BaseCommand
from backoffice import utils_proctorU_api
from backoffice.utils import get_course
from backoffice.certificate_manager.verified import get_verified_student_grades


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = """Updates the proctoru API cache for the given days
    """

    def handle(self, *args, **options):
        collection = utils_proctorU_api.get_proctoru_api_collection(drop=True)
        begin = datetime.datetime.today() - datetime.timedelta(days=200)
        end = datetime.datetime.today()
        student_activities = []


        for start, end in utils_proctorU_api.split_large_date_range(begin, end, 30):
            student_activity = utils_proctorU_api.query_api(requests.post,
                                         utils_proctorU_api.BASE_URL + utils_proctorU_api.API_URLS["client_activity_report"],
                                         utils_proctorU_api.request_infos(start, end))
            if "error" in student_activity:
                logger.error("Error between {} and {}, nothing was added".format(begin, end))
                raise student_activity["error"]

            student_activities.append(student_activity)

        logger.info("Received student activities")

        courses_grades = {}
        verified_course_ids = CourseMode.objects.filter(mode_display_name=CourseMode.VERIFIED).values_list("course_id", flat=True)
        for course_id in verified_course_ids:
            course = get_course(course_id)
            students_grades = get_verified_student_grades(course.id)
            logger.info("Computed grades for course: {}".format(course_id))
            courses_grades[course_id] = students_grades

        res = {
            "reports": student_activities,
            "grades": courses_grades,
            "last_update": datetime.datetime.now()
        }
        collection.insert(res)
        logger.info(("Data inserted in mongo -- size: reports: {}, grades: {}, "
                    "last_update: {}").format(len(res["reports"]), len(res["grades"]), res["last_update"]))
