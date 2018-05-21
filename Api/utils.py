import json

from django.http.response import HttpResponse


def method_not_allowed():
    return HttpResponse(json.dumps({
        "state": 422,
        "msg": '方法不支持',
    }))
