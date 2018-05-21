import random

from django.contrib.auth import authenticate, login, logout
from django.db.transaction import atomic
from django.contrib.auth.models import User

from Api.utils import json_response, params_error
from Api.resources import Resource
from Question.models import *


class RegistCodeResource(Resource):
    def get(self, request, *args, **kwargs):
        regist_code = random.randint(10000, 100000)
        request.session['regist_code'] = regist_code
        return json_response({
            "state": 200,
            "msg": 'OK',
            "data": {
                "regist_code": regist_code
            }
        })


class UserResource(Resource):
    def get(self, request, *args, **kwargs):
        pass

    @atomic
    def post(self, request, *args, **kwargs):
        pass

    @atomic
    def put(self, request, *args, **kwargs):
        data = request.PUT
        username = data.get('username', '')
        password = data.get('password', '')
        ensure_password = data.get('ensure_password', '')
        regist_code = data.get('regist_code', False)
        # 注册类型
        category = data.get('category', 'userinfo')

        session_regist_code = request.session.get('regist_code', '')

        # 验证用户上传数据
        errors = dict()
        # 验证用户名是否没有提供
        if not username:
            errors['username'] = '没有提供用户名'
        # 验证用户名是否已经存在
        elif User.objects.filter(username=username):
            errors['username'] = '用户名已经存在'
        # 验证密码长度
        if len(password) < 6:
            errors['password'] = '密码不可低于6位'
        # 验证密码是否匹配
        if password != ensure_password:
            errors['ensure_password'] = '密码不匹配'
        # 验证注册码是否匹配
        if regist_code != str(session_regist_code):
            errors['regist_code'] = "注册码错误"

        if errors:
            return params_error(errors)

        # 用户注册
        user = User()
        user.username = username
        # 设置密码
        user.set_password(password)
        user.save()

        if category == 'userinfo':
            userinfo = UserInfo()
            userinfo.user = user
            userinfo.name = "姓名"
            userinfo.save()
        else:
            customer = Customer()
            customer.user = user
            customer.name = "客户名称"
            customer.save()

        return json_response({
            'state': 200,
            'msg': 'OK',
            'data': {
                "user_id": user.id
            }
        })


class SessionResource(Resource):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return json_response({
                "state": 200,
                'msg': 'OK'
            })
        return json_response({
            "state": 401,
            'msg': 'require login'
        })

    def put(self, request, *args, **kwargs):
        data = request.PUT
        errors = dict()
        username = data.get('username', '')
        password = data.get('password', '')
        # 判断用户是否存在
        user = authenticate(username=username, password=password)
        if not user:
            errors['username'] = '用户名或密码错误'
            return params_error(errors)
        login(request, user)
        return json_response({
            'state': 200,
            'msg': 'OK',
        })

    def delete(self, request, *args, **kwargs):
        logout(request)
        return json_response({
            'state': 200,
            'msg': 'OK',
            "data": {
                "session": "退出成功"
            }
        })
