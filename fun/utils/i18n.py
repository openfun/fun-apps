from django.conf.global_settings import LANGUAGES

from django.utils.translation import ugettext


LANGUAGE_DICT = dict(LANGUAGES)

def language_name(language_code):
    """Language corresponding to the given code in the current language.

    Args:
        language_code (str): e.g: 'fr', 'en'
    Returns:
        language (unicode): translated name of the language. Returns the
            language code if the language was not found.
    """
    language = LANGUAGE_DICT.get(language_code)
    if language:
        return ugettext(language)
    else:
        return language_code
