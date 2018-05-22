import json
import os
from datetime import datetime, timedelta

from django.shortcuts import render
from django.db.models import Q
from django.db.transaction import atomic

from Api.resources import Resource
from Api.utils import *
from Api.decoretors import *
from Question.models import *


class QuestionnaireResource(Resource):
    # 获取客户问卷列表
    @customer_required
    def get(self, request, *args, **kwargs):
        filters = request.GET
        Qs = [Q(customer=request.user.customer)]
        try:
            if 'limit' in filters:
                limit = abs(int(filters['limit']))
                if limit > 50:
                    limit = 50
            else:
                limit = 15
            start_id = int(filters.get('start_id', 0))
            Qs.append(Q(id__gt=start_id))
            if 'state' in filters:
                Qs.append(Q(state__in=filters['state']))
            else:
                Qs.append(Q(state__in=[0, 1, 2, 3, 4]))
            if 'title' in filters:
                Qs.append(Q(title__contains=filters['title']))
        except Exception:
            return params_error({"filters": "过滤参数不合法"})
        sets = Questionnaire.objects.filter(*Qs)[:limit]
        datas = []
        for item in sets:
            dict_item = {}
            dict_item['id'] = item.id
            dict_item['title'] = item.title
            dict_item['logo'] = item.logo
            if item.datetime:
                dict_item['datetime'] = item.datetime.strftime("%Y-%m-%d")
            if item.deadline:
                dict_item['deadline'] = item.deadline.strftime("%Y-%m-%d")
            dict_item['catogory'] = item.catogory
            dict_item['state'] = item.state
            dict_item['quantity'] = item.quantity
            dict_item['background'] = item.background

            dict_item['marks'] = [{"id": mark.id, 'name': mark.name,
                                   'description': mark.description} for mark in item.marks.all()]
            dict_item['questions'] = []
            for question in item.question_set.all():
                dict_item['questions'].append(
                    {
                        'id': question.id,
                        'is_checkbox': question.is_checkbox,
                        'items': [item.content for item in question.questionitem_set.all()]
                    }
                )
            datas.append(dict_item)

        return json_response(datas)

    # 更新问卷
    @atomic
    @customer_required
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            questionnaire = Questionnaire.objects.get(
                id=int(data['id']), customer=request.user.customer, state__in=[0, 1, 2, 3])
            state = int(data.get('state', 0))
            if state not in [0, 1]:
                return params_error({
                    'state': '状态不合法'
                })
        except Exception as e:
            return params_error({
                'id': "该问卷不可修改"
            })
        questionnaire.title = data.get('title', '标题')
        questionnaire.logo = data.get('logo', 'logo')
        try:
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
        except Exception as e:
            deadline = datetime.now()+timedelta(days=10)
        questionnaire.catogory = data.get('catogory', '默认')
        questionnaire.state = state
        questionnaire.quantity = int(data.get('quantity', 1))
        questionnaire.background = data.get('background', '背景')
        questionnaire.save()
        questionnaire.marks.set(
            Mark.objects.filter(id__in=data.get('marks', [])))
        return json_response()

    # 添加问卷

    @atomic
    @customer_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        questionnaire = Questionnaire()
        questionnaire.customer = request.user.customer
        questionnaire.title = data.get('title', '标题')
        questionnaire.logo = data.get('logo', 'logo')
        questionnaire.datetime = datetime.now()
        try:
            deadline = datetime.strptime(data['deadline'], '%Y-%m-%d')
        except Exception as e:
            deadline = datetime.now()+timedelta(days=10)
        questionnaire.deadline = deadline
        questionnaire.catogory = data.get('catogory', '默认')
        questionnaire.state = 0
        questionnaire.quantity = int(data.get('quantity', 1))
        questionnaire.background = data.get('background', '背景')
        questionnaire.save()
        questionnaire.marks.set(
            Mark.objects.filter(id__in=data.get('marks', [])))
        return json_response({
            'id': questionnaire.id
        })

    # 删除问卷
    @atomic
    @customer_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        try:
            ids = data.get('ids', [])
            objs = Questionnaire.objects.filter(
                id__in=ids, state__in=[0, 1, 2, 3], customer=request.user.customer)
            deleted_ids = [obj.id for obj in objs]
            objs.delete()
        except Exception as e:
            return params_error({
                'ids': '请检查ids参数是否为列表或者检查是否有权限删除'
            })
        return json_response({
            'deleted_ids': deleted_ids
        })


class QuestionResource(Resource):
    @atomic
    @customer_required
    def post(self, request, *args, **kwargs):
        data = request.POST
        try:
            question = Question.objects.get(
                id=int(data['id']), questionnaire__customer=request.user.customer, questionnaire__state__in=[0, 1, 2, 3])
        except Exception as e:
            return params_error({
                'question': "该问题所属问卷无法修改"
            })
        question.title = data.get('title', '题纲')
        question.is_checkbox = data.get('is_checkbox', False)
        question.save()
        items = data.get('items', [])
        question.questionitem_set.all().delete()
        for item in items:
            qitem = QuestionItem()
            qitem.question = question
            qitem.content = item
            qitem.save()
        questionnaire = question.questionnaire
        questionnaire.state = 0
        questionnaire.save()
        return json_response()

    @atomic
    @customer_required
    def put(self, request, *args, **kwargs):
        data = request.PUT
        try:
            questionnaire = Questionnaire.objects.get(
                id=int(data['questionnaire_id']), customer=request.user.customer, state__in=[0, 1, 2, 3])
        except Exception as e:
            return params_error({
                'questionnaire_id': "该问卷无法修改"
            })
        question = Question()
        question.questionnaire = questionnaire
        question.title = data.get('title', '题纲')
        question.is_checkbox = data.get('is_checkbox', False)
        question.save()
        items = data.get('items', [])
        for item in items:
            qitem = QuestionItem()
            qitem.question = question
            qitem.content = item
            qitem.save()
        questionnaire.state = 0
        questionnaire.save()
        return json_response({
            'id': question.id
        })

    @atomic
    @customer_required
    def delete(self, request, *args, **kwargs):
        data = request.DELETE
        try:
            ids = data.get('ids', [])
            objs = Question.objects.filter(
                id__in=ids, questionnaire__customer=request.user.customer, questionnaire__state__in=[0, 1, 2, 3])
            deleted_ids = [obj.id for obj in objs]
            objs.delete()
        except Exception as e:
            return params_error({
                'ids': '请检查ids参数是否为列表或者检查是否有权限删除'
            })
        return json_response({
            'deleted_ids': deleted_ids
        })


class QuestionnaireCommentResource(Resource):
    @customer_required
    def get(self, request, *args, **kwargs):
        return json_response()

    @atomic
    @superuser_required
    def put(self, request, *args, **kwargs):
        return json_response()


class QuestionnaireStateResource(Resource):
    @atomic
    @customer_required
    def post(self, request, *args, **kwargs):
        return json_response()


class AnswerResource(Resource):

    @userinfo_required
    def get(self, request, *args, **kwargs):
        return json_response()

    @atomic
    @userinfo_required
    def put(self, request, *args, **kwarg):
        return json_response()

    @atomic
    @userinfo_required
    def post(self, request, *args, **kwargs):
        return json_response()

    @atomic
    @userinfo_required
    def delete(self, request, *args, **kwargs):
        return json_response()


class AnswerItemResource(Resource):
    @userinfo_required
    def get(self, request, *args, **kwargs):
        return json_response()

    @atomic
    @userinfo_required
    def put(self, request, *args, **kwargs):
        return json_response()

    @atomic
    @userinfo_required
    def post(self, request, *args, **kwargs):
        return json_response()


class QuestionnaireSuggestResource(Resource):

    @atomic
    @userinfo_required
    def put(self, request, *args, **kwargs):
        return json_response()

    @userinfo_required
    def get(self, request, *args, **kwargs):
        return json_response()


class ShareHistoryResource(Resource):
    @atomic
    @userinfo_required
    def put(self, request, *args, **kwargs):
        return json_response()

    @userinfo_required
    def get(self, request, *args, **kwargs):
        return json_response()
