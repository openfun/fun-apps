import json
import xml.etree.ElementTree as ET

from opaque_keys.edx.keys import UsageKey
from xmodule.modulestore.django import modulestore

from courseware.models import StudentModule


def fetch_all_problem_modules_from_course(course_key):
    """
    Fetch all problem modules for a course from the mongo database
    """

    qualifiers = {'qualifiers' : {'category' : 'problem'}}
    problem_modules = modulestore().get_items(course_key, **qualifiers)
    return problem_modules

def add_answers_distribution_to_problem_module(problem_module):
    """Return problem module as xml tree with answers distibution stats"""

    problem_module_as_xml = ET.fromstring(problem_module.data)
    problem_position_in_module = 0

    for element in problem_module_as_xml.iter():
        if element.tag in problem_handlers:
            problem_position_in_module += 1
            problem_handlers[element.tag](problem_module, element, problem_position_in_module)
    return problem_module_as_xml


def checkbox_handler(problem, problem_module, problem_number):
    """Handler for checkbox problem"""
    return

def text_input_handler(problem, problem_module, problem_number):
    """Handler for text input problem """
    return

def not_handled(problem, problem_module, problem_number):
    """Problem not handled yet"""
    return
    
def multiplechoice_handler(problem_module, problem, problem_position):
    """
    handle multiplechoice problem

       problem :
       <multiplechoiceresponse>
         <choicegroup label="What Apple device competed with the portable CD player?" type="MultipleChoice">
           <choice correct="false">The iPad</choice>
           <choice correct="false">Napster</choice>
           <choice correct="true">The iPod</choice>
           <choice correct="false">The vegetable peeler</choice>
         </choicegroup>
       </multiplechoiceresponse>

       Only one answer is possible, so we create a 'total_response' attribute for each choice 
       and increment it according to the student answer.
    """

    total_response = 0
   
    problem_module_id = problem_module.scope_ids.usage_id.name
    problem_module_root_id_dashed = "i4x-{}-{}-problem-".format(problem_module.scope_ids.usage_id.org,
                                                                problem_module.scope_ids.usage_id.course)

    problem_module_results = get_student_responses_to_problem_module(problem_module)


    for student_problem_module_results in problem_module_results:
        # state field contains all answers of a problem module as json
        state = json.loads(student_problem_module_results.state)
        answers = state["student_answers"]

        # get the id of a problem according to it's position in the problem_module (first problem number is 2, strange)
        question_id = problem_module_root_id_dashed + problem_module_id + "_{}_1".format(problem_position + 1)

        # get the response (remove 'choice_' string), only keep the response number
        answer = int(answers[question_id][-1:])

        ## save the student answer in the xml
        
        choices = [element for element in problem.iter('choice')]
        total_response = choices[answer].get('total_response')
        
        if total_response: # increment the attribute total_response
            total_response = int(total_response) + 1 
        else: # first student response encountered 
            total_response = 1
        # set the attribute 'total_response' to the correct value
        choices[answer].set('total_response', total_response)


def get_student_responses_to_problem_module(problem_module):
    """ Search all problem_modules in the StudentModule model"""

    course_id = problem_module.scope_ids.usage_id

    problem_module_root_id_slashed = "i4x://{}/{}/problem/".format(course_id.org, course_id.course)
    problem_module_id = problem_module.scope_ids.usage_id.name
    problem_module_state_key = UsageKey.from_string(problem_module_root_id_slashed + problem_module_id)

    # perform the request
    problem_module_results = StudentModule.objects.filter(module_state_key=problem_module_state_key)
    
    return problem_module_results
        

# this dict associate a problem type with his handler function
# We need to identify all kind of problems even if we don't do anything with it in order
# to get the question order in the module
problem_handlers = {'multiplechoiceresponse' : multiplechoice_handler,
                    'choiceresponse' : checkbox_handler,
                    'stringresponse' : text_input_handler,
                    'optionresponse' : not_handled,
                    'numericalresponse' : not_handled,
                    'customresponse' : not_handled}

            
