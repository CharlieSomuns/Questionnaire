import random
import json
from datetime import datetime

from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt

from Question.models import *
from Api.resources import Resource
# 获取注册码


class ReigstCodeResource(Resource):
    def get(self, request, *args, **kwargs):
        regist_code = random.randint(10000, 100000)
        request.session['regist_code'] = regist_code
        return HttpResponse(json.dumps({
            'regist_code': regist_code
        }), content_type="application/json")


class UserResource(Resource):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            # 判断是否是普通用户
            if hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                # 构建json字典
                data = dict()
                data['user'] = user.id
                data['age'] = getattr(userinfo, 'age', '')
                data['name'] = getattr(userinfo, 'name', '')
                data['gender'] = getattr(userinfo, 'gender', '')
                data['phone'] = getattr(userinfo, 'phone', '')
                data['email'] = getattr(userinfo, 'email', '')
                data['address'] = getattr(userinfo, 'address', '')
                if userinfo.birthday:
                    data['birthday'] = userinfo.birthday.strftime("%Y-%m-%d")
                else:
                    data['birthday'] = datetime.now().strftime("%Y-%m-%d")
                data['qq'] = getattr(userinfo, 'qq', '')
                data['wechat'] = getattr(userinfo, 'wechat', '')
                data['job'] = getattr(userinfo, 'job', '')
                data['salary'] = getattr(userinfo, 'salary', '')
                # 用json把data转化成字符串,返回给客户端
                return HttpResponse(json.dumps(data), content_type="application/json")
            # 判断是否是客户
            elif hasattr(user, 'customer'):
                customer = user.customer
                # 构建json字典
                data = dict()
                data['user'] = user.id
                data['name'] = getattr(customer, 'name', '')
                data['email'] = getattr(customer, 'email', '')
                data['company'] = getattr(customer, 'company', '')
                data['address'] = getattr(customer, 'address', '')
                data['phone'] = getattr(customer, 'phone', '')
                data['mobile'] = getattr(customer, 'mobile', '')
                data['qq'] = getattr(customer, 'qq', '')
                data['wechat'] = getattr(customer, 'wechat', '')
                data['web'] = getattr(customer, 'web', '')
                data['industry'] = getattr(customer, 'industry', '')
                data['description'] = getattr(customer, 'description', '')
                # 用json把data转化称字符串,返回给客户端
                return HttpResponse(json.dumps(data), content_type="application/json")
            else:
                # 没有相关用户信息,返回空
                return HttpResponse(json.dumps({
                    "data": {}
                }), content_type="application/json")
        # 用户未登录,不允许查看信息
        return HttpResponse(json.dumps({
            "data": {}
        }), content_type="application/json")

    def put(self, request, *args, **kwargs):
        username = request.PUT.get('username', '')
        password = request.PUT.get('password', '')
        regist_code = request.PUT.get('regist_code', '')
        session_regist_code = request.session.get('regist_code', '')
        category = request.PUT.get('category', 'userinfo')
        ensure_password = request.PUT.get('ensure_password', '')
        errors = dict()
        if not username:
            errors['username'] = '没有提供用户名'
        if User.objects.filter(username=username):
            errors['username'] = '用户名已存在'
        if len(password) < 6:
            errors['password'] = '密码长度不够'
        if password != ensure_password:
            errors['ensure_password'] = '密码不一样'
        if regist_code != str(session_regist_code):
            errors['regist_code'] = '验证码不对'
        if errors:
            return HttpResponse(json.dumps(errors), content_type='application/json')
        user = User()
        user.name = username
        user.set_password(password)
        user.save()
        if category == 'userinfo':
            userinfo = UserInfo()
            userinfo.user = user
            userinfo.name = '姓名'
            userinfo.save()
        else:
            customer = Customer()
            customer.name = '客户名称'
            customer.user = user
            customer.save()
        return HttpResponse(json.dumps({
            "msg": "创建成功",
            "user_id": user.id
        }), content_type='application/json')


# def regist_code(request):
#     regist_code = random.randint(10000, 100000)
#     request.session['regist_code'] = regist_code
#     return HttpResponse(regist_code)


# def regist_page(request):
#     return render(request, 'user/regist_page.html', {})

# # 用户注册函数


# def regist(request):
#     method = request.method
#     # 判断请求方法
#     if method == 'POST':
#         # 获取请求数据
#         data = request.POST
#         username = data.get('username', '')
#         password = data.get('password', '')
#         ensure_password = data.get('ensure_password', '')
#         regist_code = data.get('regist_code', False)
#         # 注册类型
#         category = data.get('category', 'userinfo')

#         session_regist_code = request.session.get('regist_code', '')

#         # 验证用户上传数据
#         errors = dict()
#         # 验证用户名是否没有提供
#         if not username:
#             errors['username'] = '没有提供用户名'
#         # 验证用户名是否已经存在
#         elif User.objects.filter(username=username):
#             errors['username'] = '用户名已经存在'
#         # 验证密码长度
#         if len(password) < 6:
#             errors['password'] = '密码不可低于6位'
#         # 验证密码是否匹配
#         if password != ensure_password:
#             errors['ensure_password'] = '密码不匹配'
#         # 验证注册码是否匹配
#         if regist_code != str(session_regist_code):
#             errors['regist_code'] = "注册码错误"

#         if errors:
#             return HttpResponse(json.dumps(errors), content_type="application/json")

#         # 用户注册
#         user = User()
#         user.username = username
#         # 设置密码
#         user.set_password(password)
#         user.save()

#         if category == 'userinfo':
#             userinfo = UserInfo()
#             userinfo.user = user
#             userinfo.name = "姓名"
#             userinfo.save()
#         else:
#             customer = Customer()
#             customer.user = user
#             customer.name = "客户名称"
#             customer.save()

#         return HttpResponse('注册成功')

#     return HttpResponse('注册用户')


# @csrf_exempt
# def login_user(request):
#     method = request.method
#     # 用户错误信息
#     errors = dict()
#     if method == "POST":
#         username = request.POST.get('username', '')
#         password = request.POST.get('password', '')
#     # 判断用户是否存在
#         user = authenticate(username=username, password=password)
#         if not user:
#             errors['username'] = '用户名或密码错误'
#             return HttpResponse(json.dumps(errors), content_type='application/json')
#         login(request, user)
#         return HttpResponse('登录成功')
#     else:
#         return HttpResponse('方法不支持')


# def login_page(request):
#     return render(request, 'user/login.html')


# def logout(request):
#     pass
