from django.conf.urls import url

from Api.view import *
from Api.resources import Register

api = Register()
api.regist(UserResource('user'))
api.regist(ReigstCodeResource('regist_code'))
api.regist(SessionResource('session'))
api.regist(QuestionnaireResource('questionnaire'))
