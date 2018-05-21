import json
import uuid
import os
import math

from django.http.response import HttpResponse

from QuestionNaire.settings import UPLOAD_DIR
# from Question.models import Image


# 创建一个唯一字符串
def create_uuid():
    return uuid.uuid1().hex


# 成功返回
def json_response(data={}):
    json_data = {
        'state': 200,
        'msg': 'OK',
        'data': data
    }
    json_data = json.dumps(json_data)
    return HttpResponse(json_data, content_type='application/json')


# 如果用户未登录
def not_authenticated():
    data = {
        'state': 401,
        'msg': '未登录'
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


# 如果用户没有权限
def permission_denied():
    data = {
        'state': 403,
        'msg': '没有权限'
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


# 方法不支持
def method_not_allowed():
    data = {
        'state': 405,
        'msg': '方法不支持'
    }
    return HttpResponse(json.dumps(data), content_type="application/json")


# 请求参数错误
def params_error(errors):
    return HttpResponse(json.dumps({
        'state': 422,
        'msg': '参数错误',
        'data': errors
    }), content_type="application/json")


def upload_file(path, file):
    """
    # 保存图片
    - path:保存路径,例如: userinfo/1/
    - file:客户端上传的文件,从request.FILES中读取出来
    """
    if path.startswith('/'):
        path = path[1:]
    saved_name = create_uuid()
    file_name = path
    parent_dir = os.path.join(UPLOAD_DIR, path)
    file_path = os.path.join(UPLOAD_DIR, path, saved_name)
    if not os.path.isdir(parent_dir):
        os.makedirs(parent_dir)
    with open(file_path, 'wb') as of:
        for chunk in file.chunks():
            of.write(chunk)
    return os.path.join(path, saved_name)


class PageCutter(object):
    def __init__(self, query_set, limit=15):
        self.query_set = query_set
        self.limit = limit
        all_data = query_set.all()
        count = all_data.count()
        self.pages = math.ceil(count/limit)
        self.current_page = 1
        self.count = count
