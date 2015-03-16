import csv
import datetime
import json
import xml.etree.ElementTree as ET

from django.contrib.auth.models import User, Group
from django.conf import settings

from courseware.models import StudentModule
from student.models import UserProfile
from opaque_keys.edx.keys import UsageKey
from xmodule.modulestore.django import modulestore

from course_dashboard.answers_distribution import get_problem_module, add_ancestors_names_to_problem_module
from fun import shared

def cleanup_newlines(s):
    """Makes sure all the newlines in s are representend by \r only."""
    return s.replace("\r\n", "\r").replace("\n","\r")

def write_csv(header_row, data_rows, filename, course_id):
    """write a CSV file from the contents of a datatable."""
    shared.ensure_directory_exists(settings.ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY, course_id.org, course_id.course)

    path = shared.get_safe_file_path(settings.ANSWERS_DISTRIBUTION_REPORTS_DIRECTORY,
                                course_id.org, course_id.course,
                                filename)
    ## need to encode the unico path in order to open the file in prod env    
    path = path.encode('utf-8')
    
    with open(path, "wb") as ofile:
        writer = csv.writer(ofile, quoting=csv.QUOTE_ALL)
        writer.writerow(header_row)
        for datarow in data_rows:
            encoded_row = [cleanup_newlines(unicode(s).encode('utf-8')) for s in datarow]
            writer.writerow(encoded_row)
            
def create_header_row(quizz_size):
    header_row = ['id', 'gender', 'year_of_birth', 'level_of_education']
     
    header_row += ['q' + str(i) for i in range(1, quizz_size + 1)]
    
    return header_row

PROBLEM_TYPES = ["multiplechoiceresponse", "choiceresponse" ,"stringresponse",
                 "optionresponse", "numericalresponse", "customresponse"]

def create_list_of_question_ids(organisation, course_number, problem_module_id, problem_module_size):
     question_ids = []
     i = 0;
     
     template = "i4x-{}-{}-problem-{}_".format(organisation, course_number, problem_module_id)
     question_ids = [template + str(i + 2) + "_1" for i in range(0,  problem_module_size)]
     
     return question_ids



def get_problem_module_size(problem_module):
    """
    Return the number of problem in the problem_module
    """
    
    problem_module_as_xml = ET.fromstring((problem_module.data).encode('utf-8'))
    
    problem_module_size = len([element for element in problem_module_as_xml.iter() if element.tag in PROBLEM_TYPES])
    
    return  problem_module_size

def generate_answers_distribution_report(_xmodule_instance_args, _entry_id, course_id, _task_input, action_name):
    """
    Main task to generate answer distribution as csv.

    Csv structure will be as follow: 

    'id', 'gender', 'year_of_birth', 'level_of_education', q1,      , q2       , ....
     15,     f    ,    1989        ,    m                , choice 1 , choice 2

    """
    
    store = modulestore()    
    list_problem_module = get_problem_module(course_id.to_deprecated_string(), _task_input['problem_module_id'])
    problem_module = list_problem_module[0]
    add_ancestors_names_to_problem_module(problem_module, store)
    problem_module_size = get_problem_module_size(problem_module)

    # the csv will have a header_row (name of each column) and data_rows which is (a list of data_row)
    # data_row contain all the answers of a quizz for one student    
    header_row = create_header_row(problem_module_size)
    data_rows = []
    data_row = []
    # create the full id of the quizz and questions in order to get the answer from the SQL database
    module_state_key = "i4x://{}/{}/problem/{}".format(course_id.org, course_id.course, _task_input['problem_module_id'])

    # create the full id of the quizz and questions in order to get the answer from the SQL database
    question_ids = create_list_of_question_ids(course_id.org,
                                              course_id.course,
                                              _task_input['problem_module_id'],
                                              problem_module_size)
    # instanciate a UsageKey object from the string "module_state_key"
    module_usage_key = UsageKey.from_string(module_state_key)

    # request to get all the answers to the quizz
    answers_list = StudentModule.objects.filter(module_state_key=module_usage_key)

    # iterate through the answers and fill for each student the data_row
    for answer in answers_list:
        if answer.student.is_superuser is True:
            continue
        user = answer.student
        student = UserProfile.objects.get(user=user)
        data_row = [user.id,
                    student.gender,
                    student.year_of_birth,
                    student.level_of_education]
        json_answer = json.loads(answer.state)
        for question_id in question_ids:
            try:
                data_row.append(json_answer["student_answers"][question_id])
            except KeyError:
                data_row.append("NA")
        data_rows.append(data_row)

    datetime_today = datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
    
    write_csv(header_row, data_rows,
              u"{}_{}_{}_{}_{}_{}.csv".format(datetime_today,
                                              course_id.org,
                                              course_id.course,
                                              problem_module.ancestors_names['great_grandparent'],
                                              problem_module.ancestors_names['grandparent'],
                                              problem_module.ancestors_names['parent'],
                                              problem_module.display_name).replace(' ', '-').replace('?', '-').replace('/', '-'), course_id)


    
