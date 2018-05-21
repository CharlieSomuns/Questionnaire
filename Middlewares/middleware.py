import json

from django.http.multipartparser import MultiPartParser
from django.middleware.common import MiddlewareMixin


class DataConvert(MiddlewareMixin):
    """
    # 数据类型转换
    > 因为django只能解析使用post方式上传的formdata
    > 不能够解析通过其他方法上传的json,xml,text格式数据,所以这里面,我们需要手动来解析上传的数据
    """

    def process_request(self, request):
        method = request.method

        if 'HTTP_X_METHOD' in request.META:
            method = request.META['HTTP_X_METHOD'].upper()
            if 'application/json' in request.META['CONTENT_TYPE']:
                    # 把客户端上传的json数据转化成python字典
                    data = json.loads(request.body.decode())
                    
            elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
                data=request.POST
                files=request.FILES
                setattr(request,'{method}_FILES'.format(method=method),files)
                
            setattr(request,'method',method)
            # 给request设置一个属性,属性名字就是method名称,属性值是data
            # 这样就可以在后面处理函数中直接读取请求方法对应的数据
            setattr(request,method,data)
        else:
            if method in ['PUT', 'DELETE', 'HEAD', 'OPTIONS']:
                if 'application/json' in request.META['CONTENT_TYPE']:
                    # 把客户端上传的json数据转化成python字典
                    data = json.loads(request.body.decode())
                    # 给request设置一个属性,属性名字就是method名称,属性值是data
                    # 这样就可以在后面处理函数中直接读取请求方法对应的数据
                    setattr(request, method, data)
                elif 'multipart/form-data' in request.META['CONTENT_TYPE']:
                    # 把客户端已formdata上传的数据进行解析,通常客户端会把上传的文件也放在formdata中,
                    # 所以下面的解析会把上传的文件也解析出来
                    data, files = MultiPartParser(request.META, request, request.upload_handlers).parse()
                    # 给request设置一个属性,属性名字就是method名称,属性值是data
                    # 这样就可以在后面处理函数中直接读取请求方法对应的数据
                    setattr(request,method,data)
                    # 加入客户端上传的文件,那么这里在次把上传的文件放在request的'{method}_FILES'.format(method=method)属性中,
                    # 方便后面直接读取上传的文件
                    setattr(request,'{method}_FILES'.format(method=method),files)
            
        return None
