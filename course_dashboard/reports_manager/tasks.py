import csv
import json
from time import time

from courseware.models import StudentModule
from student.models import UserProfile, anonymous_id_for_user
from instructor_task.tasks_helper import TaskProgress
from xmodule.modulestore.django import modulestore

from course_dashboard.reports_manager.utils import ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY, anonymize_username
from course_dashboard.problem_stats.utils import fetch_problem, fetch_ancestors_names, get_problem_size
from fun import shared


def write_csv(header_row, data_rows, ancestors_row, path):
    """write a CSV file from the contents of a datatable."""
    with open(path.encode('utf-8'), 'wb') as ofile:
        writer = csv.writer(ofile)
        ancestors_encoded_row = [unicode(s).encode('utf-8') for s in ancestors_row]
        writer.writerow(ancestors_encoded_row)
        writer.writerow(header_row)
        for data_row in data_rows:
            encoded_row = [unicode(s).encode('utf-8') for s in data_row]
            writer.writerow(encoded_row)

def get_path(filename, problem_location):
    shared.ensure_directory_exists(ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY,
                                   problem_location.org, problem_location.course)
    path = shared.get_safe_file_path(ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY,
                                     problem_location.org, problem_location.course,
                                     filename)
    return path

def create_header_row(problem_size):
    """
    Return the csv header row as list.
    """
    header_row = ['id', 'course_specific_id', 'gender', 'year_of_birth', 'level_of_education']
    header_row += ['q' + str(i) for i in range(1, problem_size + 1)]
    return header_row

def fetch_user_profile_data(student_module):
    """
    Return a list of user profile information. If the user profile is not
    available, the relevant pieces of information are skipped.
    """
    user = student_module.student
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None
    return  [
        anonymize_username(user.username),
        anonymous_id_for_user(user, student_module.course_id),
        unicode(user_profile.gender if user_profile else ''),
        unicode(user_profile.year_of_birth if user_profile else ''),
        unicode(user_profile.level_of_education if user_profile else '')
    ]

def fetch_student_answers(problem, problem_size):
    """ Fetch student answers and appends.
    Args:
         problem (CapaDescriptor): The course descriptor.
         problem_size (int): The problem size (number of questions).

    Returns:
         list: A list of row(list). Each row contains information about the student
         and it's answer to each question of the problem.
     """

    data_rows = []
    student_modules = StudentModule.objects.filter(module_state_key=problem.location)
    for student_module in student_modules:
        data_row = fetch_user_profile_data(student_module)
        state = json.loads(student_module.state)
        student_answers = state.get('student_answers', None)
        if not student_answers:
            continue
        for i in range(0, problem_size):
            try:
                data_row.append(student_answers["{}_{}_1".format(problem.location.html_id(),
                                                                 str(i + 2))])
            except KeyError:
                data_row.append("NA")
        data_rows.append(data_row)
    return data_rows

def generate_answers_distribution_report(_entry_id, course_descriptor, _task_input, action_name):
    """ Main task to generate answers distribution as csv.

    Csv structure will be as follow:
       'id', 'gender', 'year_of_birth', 'level_of_education', q1,      , q2
        15,     f    ,    1989        ,    m                , choice 1 , choice 2

    Args:
         _entry_id (str): Instructor task id (not used).
         course_descriptor (CourseDescriptor)
         _task_input (dict): Task input paprameters.
             E.g. : {'problem_id' : '42',
                     'running_report_name' : u"fun_course_quizz-04-05-153143.csv"}
         action_name (str) : Instructor task action name (not used).

    Returns:
         The progress state of the task (TaskProgress)
    """
    task_progress = TaskProgress(action_name, 1, time())
    task_progress.update_task_state()

    store = modulestore()
    problem = fetch_problem(store, course_descriptor, _task_input['problem_id'])
    problem_size = get_problem_size(problem)
    header_row = create_header_row(problem_size)
    data_rows = fetch_student_answers(problem, problem_size)
    ancestors_row = fetch_ancestors_names(store, problem.location)
    path = get_path(_task_input['running_report_name'], problem.location)
    write_csv(header_row, data_rows, ancestors_row, path)
    return task_progress.update_task_state({'succeeded': 1})
