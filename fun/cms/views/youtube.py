from django.http import HttpResponse, Http404
from videoproviders.api.youtube import Client

from ..utils.views import has_write_access_to_course
from util.json_request import JsonResponse


@has_write_access_to_course
def download_subtitle(request, course_key_string, subtitle_id):
    client = Client(course_key_string)
    return HttpResponse(client.download_subtitle(subtitle_id))


@has_write_access_to_course
def upload_video(request, course_key_string):
    file_obj = request.FILES.get(Client.FILE_PARAMETER_NAME)
    if not file_obj:
        raise Http404

    client = Client(course_key_string)
    result = client.upload_video(file_obj)

    return JsonResponse(result)
