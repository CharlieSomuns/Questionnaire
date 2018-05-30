"""
# 管理员接口
"""

import random
import json
import math
from datetime import datetime, timedelta

from django.shortcuts import render
from django.http.response import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.db.transaction import atomic
from django.db.models import Q
from django.utils import timezone

from Question.models import *
from Api.resources import Resource
from Api.utils import *
from Api.decorators import userinfo_required, customer_required, superuser_required


class QuestionnaireCommentResource(Resource):
    @atomic
    @superuser_required
    def put(self, request, *arg, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id')
        questionnaire_exits = Questionnaire.objects.filter(
            id=questionnaire_id, state=1)
        if not questionnaire_exits:
            return params_error({
                'questionnaire_id': '该问卷找不到,或者不可审核'
            })
        questionnaire = questionnaire_exits[0]
        is_agree = data.get('is_agree', False)
        comment = data.get('comment', '')
        if is_agree:
            questionnaire.state = 3
            questionnaire.save()
            return json_response({
                'comment': '审核通过'
            })
        if comment:
            questionnaire.state = 2
            questionnaire.save()
            questionnaire_comment = QuestionnaireComment()
            questionnaire_comment.datetime = datetime.now()
            questionnaire_comment.comment = comment
            questionnaire_comment.questionnaire = questionnaire
            questionnaire_comment.save()
            return json_response({
                'comment': '提交审核内容成功'
            })
        return params_error({
            'comment': '没有提供审核信息'
        })
