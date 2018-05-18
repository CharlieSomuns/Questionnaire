from django.conf.urls import url

from Api.view import *

# 注册url
urlpatterns = [
    url(r'^regist$', regist),
    url(r'^regist_code$', regist_code),
    url(r'^regist_page$', regist_page),
]
