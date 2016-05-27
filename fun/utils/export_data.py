import csv
from datetime import datetime
from StringIO import StringIO

from django.http import HttpResponse


def csv_response(header_row, data_rows, filename):
    def encode_data(data):
        if isinstance(data, unicode):
            return data.encode('utf-8')
        elif isinstance(data, datetime):
            return data.strftime('%Y/%m/%d')
        else:
            return u"{}".format(data)

    response_content = StringIO()
    writer = csv.writer(response_content)
    writer.writerow([field.encode('utf-8') for field in header_row])
    for data_row in data_rows:
        writer.writerow([encode_data(d) for d in data_row])
    response_content.seek(0)

    response = HttpResponse(response_content.read(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    return response
