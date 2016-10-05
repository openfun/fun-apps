import logging
import pycaption
import requests

from django.conf import settings
from django.core.cache import caches


SUBTITLE_CACHE = caches["video_subtitles"]

logger = logging.getLogger(__name__)


def get_vtt_content(url):
    """Get the content of a subtitle file converted to WebVTT format.

    A caching strategy based on the url of the subtitle file is setup so that
    we don't have to redownload the files every time.

    Args:
        url (str): may point to e.g. an srt file.

    Returns:
        caps (unicode): vtt-formatted subtitles content. Returns None if
            subtitles could not be converted to VTT or if the original subtitle
            file exceeds SUBTITLE_MAX_BYTES.
    """
    caps = SUBTITLE_CACHE.get(url)
    if caps is None:
        response = requests.get(url, stream=True)
        if response.status_code < 400:
            # Maximum subtitle file size, in bytes
            subtitle_max_bytes = getattr(settings, "SUBTITLES_MAX_BYTES", 5*1024*1024)
            content = ""
            for chunk in response.iter_content(chunk_size=1024):
                content += chunk
                if len(content) > subtitle_max_bytes:
                    logger.error("Trying to load large subtitle file from %s", url)
                    content = ""
                    break
            caps = convert_to_vtt(content) if content else ""
            if caps is not None:
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
