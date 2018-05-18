import random
import json

from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User

from Question.models import *

# 获取注册码


def regist_code(request):
    regist_code = random.randint(10000, 100000)
    request.session['regist_code'] = regist_code
    return HttpResponse(regist_code)


def regist_page(request):
    return render(request, 'user/regist_page.html', {})

# 用户注册函数


def regist(request):
    method = request.method
    # 判断请求方法
    if method == 'POST':
        # 获取请求数据
        data = request.POST
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
            return HttpResponse(json.dumps(errors), content_type="application/json")

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

        return HttpResponse('注册成功')

    return HttpResponse('注册用户')
