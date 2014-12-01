import os

from django.conf import settings
from django.test.utils import override_settings
from django.views.decorators.csrf import csrf_exempt

import ckeditor.views


@csrf_exempt
def ckeditor_upload(request):
    with override_settings(CKEDITOR_UPLOAD_PATH=get_upload_path()):
        return ckeditor.views.upload(request)


def ckeditor_browse(request):
    with override_settings(CKEDITOR_UPLOAD_PATH=get_upload_path()):
        return ckeditor.views.browse(request)


def get_upload_path():
    return os.path.join(settings.CKEDITOR_UPLOAD_PATH, "news")
