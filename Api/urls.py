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
api.regist(PasswordResource('password'))

# 客户
api.regist(CustomerQuestionnaireResource('customer_questionnaire'))
api.regist(CustomerQuestionResource('customer_question'))
api.regist(CustomerQuestionnaireStateResource('questionnaire_state'))
api.regist(CustomerQuestionIndexResource('question_index'))

# 管理员
api.regist(QuestionnaireCommentResource('questionnaire_comment'))
api.regist(AdminQuestionnaireResource('admin_questionnaire'))

# 用户
api.regist(JoinQuestionnaireResource('questionnaire_join'))
api.regist(AnswerQuestionnaireResource('questionnaire_answer'))
