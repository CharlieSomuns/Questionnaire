from Api.utils import *

# 登录用户必须为客户


def customer_required(func):
    def _wrapper(request, *args, **kwarg):
        if not request.user.is_authenticated:
            return not_authenticated()
        user = request.user
        if not hasattr(user, 'customer'):
            return permission_denied()
        return func(request, *args, **kwarg)
    return _wrapper


# 登录用户必须为普通用户
def userinfo_required(func):
    def _wrapper(request, *args, **kwarg):
        if not request.user.is_authenticated:
            return not_authenticated()
        user = request.user
        if not hasattr(user, 'userinfo'):
            return permission_denied()
        return func(request, *args, **kwarg)
    return _wrapper
