import json
import copy

from django.utils.deprecation import MiddlewareMixin
from django.http.multipartparser import MultiPartParser


class MethodConvertMiddleware(MiddlewareMixin):
    def process_request(self, request):
        method = request.method
        if 'HTTP_X_METHOD' in request.META:
            method = request.META['HTTP_X_METHOD'].upper()
            if 'application/json' in request.META['CONTENT_TYPE']:
                data = json.loads(request.body.decode())
            elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
                data = request.POST
                files = request.FILES
                setattr(request, method.upper()+'_FILES', files)
            setattr(request, 'method', method)
            setattr(request, method.upper(), data)
        else:
            if method in ['PUT', 'DELETE', 'HEAD', 'OPTIONS']:
                if 'application/json' in request.META['CONTENT_TYPE']:
                    POST = json.loads(request.body.decode())
                    setattr(request, method.upper(), POST)
                elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
                    data, files = MultiPartParser(
                        request.META, request, request.upload_handlers).parse()
                    setattr(request, method.upper()+'_FILES', files)
                    setattr(request, method.upper(), data)
