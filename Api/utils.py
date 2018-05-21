import json
import uuid
import os

from django.http.response import HttpResponse

from QuestionNaire.settings import BASE_DIR
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
def require_login():
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


# def upload_img(path, file):
#     """
#     # 保存图片
#     - path:保存路径,例如: product/1/
#     - file:客户端上传的文件,从request.FILES中读取出来
#     """
#     saved_name = create_uuid()
#     parent_dir = os.path.join(BASE_DIR, 'Upload', path)
#     file_path = os.path.join(BASE_DIR, 'Upload', path, saved_name)
#     if not os.path.isdir(parent_dir):
#         os.makedirs(parent_dir)
#     with open(file_path, 'wb') as of:
#         for chunk in file.chunks():
#             of.write(chunk)
#     img = Image()
#     img.path = path+saved_name
#     img.size = file.size
#     img.filename = file.name
#     img.saved_name = saved_name
#     img.save()
#     return img
