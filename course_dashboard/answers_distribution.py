import json
import xml.etree.ElementTree as ET

from opaque_keys.edx.keys import UsageKey
from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore.django import modulestore

from courseware.models import StudentModule
from xmodule.modulestore import mixed

def fetch_all_problem_modules_from_course(course_key, store):
    """
    Fetch all problem modules for a course from the mongo database
    """

    qualifiers = {'qualifiers' : {'category' : 'problem'}}
    problem_modules = store.get_items(course_key, **qualifiers)
    return problem_modules

def add_ancestors_names_to_problem_module(problem_module, store):
    
    ancestors_names = {'parent' : '',
                       'grandparent' : '',
                       'great_grandparent' : ''}
    

    parent = store.get_parent_location(problem_module.location)
    if parent:
        ancestors_names['parent'] = store.get_item(parent).display_name
        grandparent = store.get_parent_location(parent)
        if grandparent:
            ancestors_names['grandparent'] = store.get_item(grandparent).display_name
            great_grandparent = store.get_parent_location(grandparent)
            if great_grandparent:
                ancestors_names['great_grandparent'] = store.get_item(great_grandparent).display_name
    problem_module.ancestors_names = ancestors_names


def parse_problem_data_from_problem_module(problem_module):
    problem_module_as_xml = ET.fromstring((problem_module.data).encode('utf-8'))
    problem_module.as_xml = problem_module_as_xml

def add_answers_distribution_to_problem_module(problem_module):
    """Return problem module as xml tree with answers distibution stats"""

    problem_module.as_xml = ET.fromstring((problem_module.data).encode('utf-8'))
    problem_position_in_module = 0

    for element in problem_module.as_xml.iter():
        if element.tag in PROBLEM_HANDLERS:
            problem_position_in_module += 1
            PROBLEM_HANDLERS[element.tag](problem_module, element, problem_position_in_module)

    
def multiplechoice_handler(problem_module, problem, problem_position):
    """
    handle multiplechoice problem

       problem :(xml.etree.ElementTree)
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

       problem_module (CapaDescriptorWithMixinspr)
    """

    total_response = 0
    problem_module_id = problem_module.scope_ids.usage_id.name
    problem_module_root_id_dashed = "i4x-{}-{}-problem-".format(problem_module.scope_ids.usage_id.org,
                                                                problem_module.scope_ids.usage_id.course)

    problem_module_results = get_student_responses_to_problem_module(problem_module)

    for student_problem_module_results in problem_module_results:
        # state field contains all answers of a problem module as json
        state = json.loads(student_problem_module_results.state)
        try:
            answers = state.get("student_answers", {})
            if not answers:
                continue
        except KeyError :
            # happen when a student has loaded the problem but not yet answerd
            continue

        # get the id of a problem according to it's position in the problem_module (first problem number is 2, strange)
        question_id = problem_module_root_id_dashed + problem_module_id + "_{}_1".format(problem_position + 1)
        # get the response (remove 'choice_' string), only keep the response number
        try:
            answer = int(answers[question_id][-1:])
        except KeyError :
            # happen when a student has loaded the problem answer at least one question but not the one we search
            continue

        ## save the student answer in the xml
        
        choices = [element for element in problem.iter('choice')]
        total_response = choices[answer].get('total_response')
        
        if total_response: # increment the attribute total_response
            total_response = int(total_response) + 1 
        else: # first student response encountered 
            total_response = 1
        # set the attribute 'total_response' to the correct value
        choices[answer].set('total_response', total_response)

    ## All student result have been add to total_response, now calculate percentage for each different choice
    add_global_info_to_multiplechoice_problem(problem)

def get_student_responses_to_problem_module(problem_module):
    """ Search all problem_modules in the StudentModule model"""

    course_id = problem_module.scope_ids.usage_id

    problem_module_root_id_slashed = "i4x://{}/{}/problem/".format(course_id.org, course_id.course)
    problem_module_id = problem_module.scope_ids.usage_id.name
    problem_module_state_key = UsageKey.from_string(problem_module_root_id_slashed + problem_module_id)

    # perform the request
    problem_module_results = StudentModule.objects.filter(module_state_key=problem_module_state_key)
    
    return problem_module_results

def add_global_info_to_multiplechoice_problem(problem):
    
    total_responses_count = sum([int(choice.get("total_response", "0")) for choice in problem.iter('choice')])
    
    problem.set('total_response', total_responses_count)

    # based on the total_response_count write a percentage for each choice
    for choice in problem.iter('choice'):
        if choice.get("total_response"):
            per = round(float(choice.get("total_response")) * (100.0 / total_responses_count), 2)
            choice.set('percentage_response', per)
        else:
            choice.set('percentage_response', 0)
            
not_handled = lambda problem, problem_module, problem_number: None
          
# this dict associate a problem type with his handler function
# We need to identify all kind of problems even if we don't do anything with it in order
# to get the question order in the module
PROBLEM_HANDLERS = {'multiplechoiceresponse' : multiplechoice_handler,
                    'choiceresponse' : not_handled,
                    'stringresponse' : not_handled,
                    'optionresponse' : not_handled,
                    'numericalresponse' : not_handled,
                    'customresponse' : not_handled}

            
def get_problem_module(course_key_string, problem_module_id):

    course_key = CourseKey.from_string(course_key_string)
    store = modulestore()
    qualifiers = {'qualifiers' : {'category' : 'problem',
                                  'name' : problem_module_id}}
    return store.get_items(course_key, **qualifiers)
    

