import random
from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.db.transaction import atomic
from django.contrib.auth.models import User

from Api.utils import *
from Api.resources import Resource
from Question.models import *


class RegistCodeResource(Resource):
    def get(self, request, *args, **kwargs):
        regist_code = random.randint(10000, 100000)
        request.session['regist_code'] = regist_code
        return json_response({
            "regist_code": regist_code
        })


class UserResource(Resource):
    # 获取用户信息
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
                birthday = userinfo.birthday
                if birthday:
                    data['birthday'] = birthday.strftime("%Y-%m-%d")
                else:
                    data['birthday'] = datetime.now().strftime("%Y-%m-%d")
                data['qq'] = getattr(userinfo, 'qq', '')
                data['wechat'] = getattr(userinfo, 'wechat', '')
                data['job'] = getattr(userinfo, 'job', '')
                data['salary'] = getattr(userinfo, 'salary', '')
                # 用json把data转化成字符串,返回给客户端
                return json_response(data)
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
                return json_response(data)
            else:
                # 没有相关用户信息,返回空
                return json_response({})
        # 用户未登录,不允许查看信息
        return not_authenticated()

    # 更新用户信息

    @atomic
    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            user = request.user
            # 判断是否是普通用户
            data = request.POST
            if hasattr(user, 'userinfo'):
                userinfo = user.userinfo
                userinfo.name = data.get('name', '姓名')
                userinfo.age = data.get('age', 1)
                userinfo.gender = data.get('gender', 'male')
                userinfo.phone = data.get('phone', '')
                userinfo.email = data.get('email', '')
                userinfo.address = data.get('address', '')
                try:
                    birthday = datetime.strptime(
                        data.get('birthday', ''), "%Y-%m-%d")
                except Exception:
                    birthday = datetime.strptime('2018-01-01', "%Y-%m-%d")
                userinfo.birthday = birthday
                userinfo.qq = data.get('qq', '')
                userinfo.wechat = data.get('wechat', '')
                userinfo.job = data.get('job', '')
                userinfo.salary = data.get('salary', '')
                # 这里还没有保存图片
                userinfo.save()

            elif hasattr(user, 'customer'):
                customer = user.customer
                customer.name = data.get('name', '客户名称')
                customer.email = data.get('email', '')
                customer.company = data.get('company', '')
                customer.address = data.get('address', '')
                customer.phone = data.get('phone', '')
                customer.mobile = data.get('mobile', '')
                customer.qq = data.get('qq', '')
                customer.wechat = data.get('wechat', '')
                customer.web = data.get('web', '')
                customer.industry = data.get('industry', '')
                customer.description = data.get('description', '')
                customer.save()
            else:
                return json_response({})
            return json_response({})
        return not_authenticated()

    # 注册用户
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
            "user_id": user.id
        })


class SessionResource(Resource):
    # 获取session信息
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return json_response({
                "user_id": request.user.id
            })
        return not_authenticated()

    # 用户登录
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
            "session": "登录成功"
        })

    # 用户退出
    def delete(self, request, *args, **kwargs):
        logout(request)
        return json_response({
            "session": "退出成功"
        })
