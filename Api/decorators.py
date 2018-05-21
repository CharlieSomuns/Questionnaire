from Api.utils import permission_denied


def customer_required(func):
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'customer'):
            return func(self, request, *args, **kwargs)
        return permission_denied()
    return _wrapper


def userinfo_required(func):
    def _wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated and hasattr(request.user, 'userinfo'):
            return func(self, request, *args, **kwargs)
        return permission_denied()
    return _wrapper
