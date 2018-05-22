from django.conf.urls import url

from Api.common import *
from Api.questionnaire import *
from Api.resources import Register


api = Register()
api.regist(RegistCodeResource('regist_code'))
api.regist(UserResource('user'))
api.regist(SessionResource('session'))

api.regist(QuestionnaireResource('customer_questionnaire'))
api.regist(QuestionResource('customer_question'))
api.regist(QuestionnaireCommentResource('questionnaire_comment'))
api.regist(QuestionnaireStateResource('questionnaire_state'))
api.regist(AnswerResource('answer'))
api.regist(AnswerItemResource('answer_item'))
api.regist(QuestionnaireSuggestResource('questionnaire_suggest'))
api.regist(ShareHistoryResource('share_history'))