import json
import copy

from django.utils.deprecation import MiddlewareMixin
from django.http.multipartparser import MultiPartParser


class MethodConvertMiddleware(MiddlewareMixin):
    def process_request(self, request):
        method = request.method.upper()
        if 'application/json' in request.META['CONTENT_TYPE']:
            data = json.loads(request.body.decode())
        elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
            data, files = MultiPartParser(
                request.META, request, request.upload_handlers).parse()
            setattr(request, method.upper()+'_FILES', files)
        else:
            data = {}
        setattr(request, method, data)
        if 'HTTP_X_METHOD' in request.META:
            setattr(request, 'method', method)
