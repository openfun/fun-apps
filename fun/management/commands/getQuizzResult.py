# pylint: disable=missing-docstring

import json
import csv
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group

from courseware.models import StudentModule
from student.models import UserProfile

from opaque_keys.edx.keys import UsageKey

##
##  Csv functions
##

def cleanup_newlines(s):
    """Makes sure all the newlines in s are representend by \r only."""
    return s.replace("\r\n","\r").replace("\n","\r")

def return_csv(header_row, data_rows, filename):
    """Outputs a CSV file from the contents of a datatable."""
    ofile  = open(filename, "wb")
    writer = csv.writer(ofile, dialect='excel', quotechar='"', quoting=csv.QUOTE_ALL)
    writer.writerow(header_row)
    for datarow in data_rows:
        encoded_row = [cleanup_newlines(unicode(s).encode('utf-8')) for s in datarow]
        writer.writerow(encoded_row)
    print "Operation succeed, " + filename + " has just been created"


##
##   Command that will dump the answers of a quizz
##

class Command(BaseCommand):
    help = """

             Command to dump the result of a quizz

             Usage : <--organisation ORGANISATION --course_number COURSE_NUMBER --quizz_id QUIZZ_ID --quizz_size QUIZZ_SIZE [--output_file_name FILENAME] [--demography] >

             To use it 4 arguments are mandatory
                1 - the organisation name
                2 - the course number
                3 - the quizz id [to get it export the mooc and untar it. in the directory /problem you will find the id of each quizz as id.xml ]
                4 - the quizz size (the number of questions in the quizz)
              2 arguments are optional
                1 - output_file_name :  you can name the output file (by defaut the file name is the quizz id)
                2 - demography : to get demographic information about the student (gender, age, level of education)

           """

    option_list = BaseCommand.option_list + (
        make_option('--organisation',
                    action = 'store',
                    dest = 'organisation',
                    type = 'string'
                    ),
        make_option('--course_number',
                    action = 'store',
                    dest='course_number',
                    type = 'string'
                    ),
        make_option('--quizz_id',
                    action = 'store',
                    dest = 'quizz_id',
                    type = 'string'
                    ),
        make_option('--quizz_size',
                    action = 'store',
                    dest = 'quizz_size',
                    type = 'int'
                    ),
        make_option('--demography',
                    action = 'store_true',
                    dest = 'demography',
                    default = False,
                   ),
        make_option('--output_file_name',
                    action = 'store',
                    dest = 'output_file_name',
                    default = False,
                   ),
        )

    def create_header_row(self, quizz_size, demography):
        header_row = []
        i = 0;

        if (demography):
            header_row.append('id')
            header_row.append('gender')
            header_row.append('year_of_birth')
            header_row.append('level_of_education')
        while i < quizz_size:
            header_row.append( 'q' + str(i + 1))
            i += 1
        return header_row

    def create_list_of_question_id(self, organisation, course_number, quizz_id, quizz_size):
        question_ids = []
        i = 0;

        while i < quizz_size:
            question_ids.append( "i4x-" + organisation + "-" + course_number +  "-problem-" + quizz_id + "_" + str((i + 2))+ "_1")
            i += 1
        return question_ids


    def handle(self, *args, **options):

        if not all([options['organisation'], options['course_number'], options['quizz_size'],
                    options['quizz_size']]):
             raise CommandError('all arguments are mandatory')

        if not options['output_file_name'] :
            options['output_file_name'] = options['quizz_id']

        # the csv will have a header_row (name of each column) and data_rows which is (a list of data_row)
        # data_row contain all the answers of a quizz for one student (if 'demography' option is true the date_row contains also demographic information about the student)
        header_row = self.create_header_row(options['quizz_size'], options['demography'])
        data_rows = []
        data_row = []

        # create the full id of the quizz and questions in order to get the answer from the SQL database

        module_state_key = "i4x://" + options['organisation'] + "/" + options['course_number'] +  "/problem/" + options['quizz_id']
        question_ids = self.create_list_of_question_id(options['organisation'],
                                                  options['course_number'],
                                                  str(options['quizz_id']),
                                                  options['quizz_size'])

        # instanciate a UsageKey object from the string "module_state_key"
        module_usage_key = UsageKey.from_string(module_state_key)

        # request to get all the answers to the quizz
        answers_list = StudentModule.objects.filter(module_state_key = module_usage_key)

        # iterate through the answers and fill for each student the data_row
        for answer in answers_list:
            if (answer.student.is_superuser is not True):

                if (options['demography']):
                    student = UserProfile.objects.get(user = answer.student)
                    data_row = [student.id, student.gender,
                                student.year_of_birth, student.level_of_education]
                else:
                    data_row = []

                json_answer = json.loads(answer.state)

                for question_id in question_ids:
                    try:
                        data_row.append(json_answer["student_answers"][question_id])
                    except KeyError:
                        data_row.append("NA")
                data_rows.append(data_row)
        return_csv(header_row, data_rows, options['output_file_name']  + ".csv")
