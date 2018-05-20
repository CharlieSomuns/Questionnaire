import json
import copy

from django.utils.deprecation import MiddlewareMixin
from django.http.multipartparser import MultiPartParser


class CommonMiddleware(MiddlewareMixin):
    def process_request(self, request,):
        pass

    def process_response(self, request, response):
        pass


class MethodConvertMiddleware(MiddlewareMixin):
    def process_request(self, request):
        method = request.method
        if 'HTTP_X_METHOD' in request.META:
            method = request.META['HTTP_X_METHOD'].upper()
        else:
            if method in ['PUT', 'DELETE', 'HEAD', 'OPTIONS']:
                if 'application/json' in request.META['CONTENT_TYPE']:
                    POST = json.loads(request.body.decode())
                    setattr(request, method.upper(), POST)
                elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
                    POST, FILES = MultiPartParser(
                        request.META, request, request.upload_handlers).parse()
                    setattr(request, method.upper()+'_FILES', FILES)
                    setattr(request, method.upper(), POST)
                else:
                    setattr(request, method.upper(), {})

