from django.conf.urls import url

from Api.common import *
from Api.user import *
from Api.admin import *
from Api.customer import *

from Api.resources import Register

api = Register()
# 通用接口
api.regist(ReigstCodeResource('regist_code'))
api.regist(UserResource('user'))
api.regist(SessionResource('session'))
api.regist(QuestionnaireResource('questionnaire'))

# 客户
api.regist(CustomerQuestionnaireResource('customer_questionnaire'))
api.regist(CustomerQuestionResource('customer_question'))
api.regist(CustomerQuestionnaireStateResource('questionnaire_state'))

# 管理员
api.regist(QuestionnaireCommentResource('questionnaire_comment'))

# 用户
api.regist(JoinQuestionnaireResource('questionnaire_join'))
api.regist(AnswerQuestionnaireResource('questionnaire_answer'))

