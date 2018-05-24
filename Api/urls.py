from django.conf.urls import url

from Api.view import *
from Api.resources import Register

api = Register()
api.regist(UserResource('user'))
api.regist(ReigstCodeResource('regist_code'))
api.regist(SessionResource('session'))
api.regist(QuestionnaireResource('customer_questionnaire'))
api.regist(QuestionResource('customer_question'))
api.regist(QuestionnaireCommentResource('questionnaire_comment'))
api.regist(QuestionnaireStateResource('questionnaire_state'))
api.regist(AnswerResource('answer'))
api.regist(AnswerItemResource('answer_item'))
api.regist(CommentQuestionnaire('questionnaire'))
api.regist(HomeQuestionnaireResource('home_questionnaire'))
api.regist(UserQuestionnaireResource('user_questionnaire'))
