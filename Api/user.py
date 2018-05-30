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


class JoinQuestionnaireResource(Resource):
    @atomic
    @userinfo_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        questionnaire_id = data.get('questionnaire_id', 0)
        # 找出要参与的问卷
        questionnaire_exits = Questionnaire.objects.filter(
            id=questionnaire_id, state=4)
        if not questionnaire_exits:
            return params_error({
                'questionnaire_id': '当前问卷不存在'
            })

        # 判断是否已经参与了该问卷
        questionnaire = questionnaire_exits[0]
        has_joined = Answer.objects.filter(
            userinfo=request.user.userinfo, questionnaire=questionnaire)
        if has_joined:
            return params_error({
                'questionnaire_id': '已经参与了该问卷调查'
            })
        # 判断参与问卷的人数是否已满
        has_joined_count = Answer.objects.filter(
            questionnaire=questionnaire).count()
        if questionnaire.quantity <= has_joined_count:
            return params_error({
                'questionnaire_id': '该问卷参与人数已满'
            })
        # 判断问卷是否已经结束
        #  datetime.now() 不带时区 而从数据库中读取出来的时间是带时区的所以不能直接比较
        # 要使用django.utils timezone.now()
        if questionnaire.deadline < timezone.now():
            return params_error({
                'questionnaire_id': '该问卷已结束'
            })
        # 创建参与信息
        answer = Answer()
        answer.userinfo = request.user.userinfo
        answer.questionnaire = questionnaire
        answer.datetime = datetime.now()
        answer.is_done = False
        answer.save()
        # 更新可用问卷数量
        questionnaire.free_count = questionnaire.free_count-1
        questionnaire.save()

        return json_response({
            'id': answer.id
        })

    @atomic
    @userinfo_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        ids = data.get('ids', [])
        objs = Answer.objects.filter(
            id__in=ids, userinfo=request.user.userinfo, is_done=False)
        deleted_ids = [obj.id for obj in objs]
        # 更新问卷可用数量
        for obj in objs:
            questionnaire = obj.questionnaire
            questionnaire.free_count = questionnaire.free_count+1
            questionnaire.save()
        objs.delete()
        return json_response({
            'deleted_ids': deleted_ids
        })

    @userinfo_required
    def get(self, request, *args, **kwargs):
        data = request.GET
        limit = abs(int(data.get('limit', 30)))
        start_id = data.get('start_id', 0)
        is_done = data.get('is_done', False)
        objs = Answer.objects.filter(
            id__gt=start_id, userinfo=request.user.userinfo, is_done=is_done)

        data = []
        for obj in objs:
            answer_dict = dict()
            answer_dict['id'] = obj.id
            answer_dict['create_time'] = datetime.strftime(
                obj.datetime, '%Y-%m-%d')
            answer_dict['is_done'] = obj.is_done
            answer_dict['questionnaire'] = {
                'id': obj.questionnaire.id,
                'title': obj.questionnaire.title
            }
            data.append(answer_dict)

        return json_response(data)


class AnswerQuestionnaireResource(Resource):

    def _save_answers(self, data, request):
         # 判断问卷是否存在
        questionnaire_id = data.get('questionnaire_id', 0)
        questionnaire_exist = Questionnaire.objects.filter(
            id=questionnaire_id, state=4, deadline__gt=timezone.now())
        if not questionnaire_exist:
            return params_error({
                "questionnaire_id": "问卷不存在,或者不可提交答案"
            })
        # 验证问卷是否可以提交答案
        questionnaire = questionnaire_exist[0]
        has_joined = Answer.objects.filter(
            questionnaire=questionnaire, userinfo=request.user.userinfo, is_done=False)
        if not has_joined:
            return params_error({
                'questionnaire_id': "还没有参与该问卷,或者该问卷已经完成"
            })

        questions = data.get('questions', [])

        # 可以提交答案的问题
        question_ids = [item['question_id'] for item in questions]
        questions_can_answer = Question.objects.filter(
            id__in=question_ids, questionnaire=questionnaire)
        questions_can_answer_ids = [obj.id for obj in questions_can_answer]
        # 如果有回答过该问题,那么清空该问题答案
        AnswerItem.objects.filter(
            question__in=questions_can_answer, userinfo=request.user.userinfo).delete()

        # data=[
        #   {
        #       "question_id":id,
        #       "items":[1,2,3]
        #   }
        # ]

        # 将用户的选项保存下来
        for question in questions:
            # 判断提交的问题是否合法
            if question['question_id'] in questions_can_answer_ids:
                question_obj = Question.objects.get(id=question['question_id'])
                answer = AnswerItem()
                answer.question = question_obj
                answer.userinfo = request.user.userinfo
                # 把该问题下选项找出来
                items = QuestionItem.objects.filter(
                    id__in=question['items'], question=question_obj)
                if items.count() > 1 and question_obj.is_checkbox:
                    answer.save()
                    answer.items.set(items)
                elif items.count() == 1:
                    answer.save()
                    answer.items.set(items)
                else:
                    return json_response({
                        "warnning": '参数错误'
                    })

        # 用户保存,或者提交答案
        answer = has_joined[0]
        is_done = data.get('is_done', False)
        answer.is_done = is_done
        answer.save()

        return json_response({'msg': "提交成功"})

    @atomic
    @userinfo_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        response = self._save_answers(data, request)
        return response

    @atomic
    @userinfo_required
    def post(self, request, *args, **kwargs):
        data = request.POST
        response = self._save_answers(data, request)
        return response

    @userinfo_required
    def get(self, request, *args, **kwargs):
        data = request.GET
        questionnaire_id = data.get('questionnaire_id', 0)
        has_joined = Answer.objects.filter(
            userinfo=request.user.userinfo, questionnaire__id=questionnaire_id)
        if not has_joined:
            return params_error({
                'questionnaire_id': "没有相关信息"
            })
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
        answers = AnswerItem.objects.filter(
            userinfo=request.user.userinfo, question__questionnaire=questionnaire)
        data = [
            {
                "question_id": answer.question.id,
                "title": answer.question.title,
                "items": [{'id': item.id,'content':item.content} for item in answer.items.all()]
            } for answer in answers
        ]

        return json_response(data)

