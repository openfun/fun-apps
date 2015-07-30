import pycaption
import requests

from django.core.cache import get_cache


SUBTITLE_CACHE = get_cache("video_subtitles")


def get_vtt_content(url):
    """Get the content of a subtitle file converted to WebVTT format.

    A caching strategy based on the url of the subtitle file is setup so that
    we don't have to redownload the files every time.

    Args:
        url (str): may point to e.g. an srt file.

    Returns:
        caps (unicode): vtt-formatted subtitles content. Returns None if
            subtitles could not be converted to VTT.
    """
    caps = SUBTITLE_CACHE.get(url)
    if not caps:
        response = requests.get(url)
        if response.status_code < 400:
            caps = convert_to_vtt(response.content)
            if caps:
                SUBTITLE_CACHE.set(url, caps, 24*60*60)
    return caps

def convert_to_vtt(caps):
    """Convert subtitles to WebVTT format

    Note that if the subtitles are already in VTT format, nothing is done.

    Args:
        caps (str or unicode)
    Returns:
    caps (unicode): None if the format could not be detected.
    """
    if isinstance(caps, str):
        caps = caps.decode('utf-8')
    caps = caps.strip(u"\ufeff").strip(u"\n").strip(u"\r")
    sub_reader = pycaption.detect_format(caps)
    if sub_reader is None:
        return None
    if sub_reader != pycaption.WebVTTReader:
        caps = pycaption.WebVTTWriter().write(sub_reader().read(caps))
    return caps
