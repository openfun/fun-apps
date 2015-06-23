import sys
from path import path

MICROSITE_ROOT_DIR = path("/edx/app/edxapp/fun-microsites")

def get_microsite_configuration(hostname):
    """
    Return the microsite configuration with properly defined hostnames. The
    value returned is suitable for the MICROSITE_CONFIGURATION variable.
    """
    sys.path.append(MICROSITE_ROOT_DIR)
    import fun_microsites
    configuration = fun_microsites.get_configuration(hostname)
    sys.path.pop()
    return configuration
