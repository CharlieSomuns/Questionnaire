from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponse
from django.conf import settings
from django.conf.urls import url

from Api.utils import method_not_allowed, json_response


class Resource(object):
    """
    # 资源
    Api下所有的资源继承自本类;
    所有类为单例模式
    enter方法是资源的入口,根据method类型分别调用不同的处理方法
    """

    def __init__(self, name=None):
        """
        - name 资源名称
        例如: session
        """
        self.name = name or self.__class__.__name__.lower()

    def enter(self, request, *args, **kwargs):
        """
        # 请求的入口
        """
        method = request.method
        try:
            if method == 'GET':
                response = self.get(request, *args, **kwargs)
            elif method == 'POST':
                response = self.post(request, *args, **kwargs)
            elif method == 'PUT':
                response = self.put(request, *args, **kwargs)
            elif method == 'DELETE':
                response = self.delete(request, *args, **kwargs)
            elif method == 'OPTIONS':
                response = self.options(request, *args, **kwargs)
            elif method == 'HEAD':
                response = self.head(request, *args, **kwargs)
            else:
                response = method_not_allowed()
        except Exception as e:
            if settings.DEBUG:
                raise
            else:
                response = json_response({
                    'state': 500,
                    'msg': '服务器发生错误'
                })
        return response

    def get(self, request, *args, **kwarg):
        return method_not_allowed()

    def post(self, request, *args, **kwarg):
        return method_not_allowed()

    def put(self, request, *args, **kwarg):
        return method_not_allowed()

    def delete(self, request, *args, **kwarg):
        return method_not_allowed()

    def head(self, request, *args, **kwargs):
        return method_not_allowed()

    def options(self, request, *args, **kwargs):
        return method_not_allowed()


class Register(object):
    """
    # 注册器  

    默认接受一个接口版本号v1,可以自定义版本号

    在跟路由中使用方式:  
    url(r'^api/',include(register.urls))
    """

    def __init__(self, version='v1'):
        self.version = version
        self.resources = []

    def regist(self, resource):
        """
        # 注册资源
        """
        if not isinstance(resource, Resource):
            raise Exception('resource 必须继承自 Resource,并且是一个Resource对象')
        else:
            self.resources.append(resource)

    @property
    def urls(self):
        """
        # 绑定已注册资源的url
        """
        urlpatterns = []
        for resource in self.resources:
            urlpatterns.append(url(r'^{version}/{name}$'.format(version=self.version, name=resource.name),  csrf_exempt(resource.enter)))
        return urlpatterns
