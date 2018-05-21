import json
import os
from datetime import datetime

from django.db.models import Q
from django.db.transaction import atomic

from Api.resources import Resource
from Api.utils import *
from Api.decoretors import *
from Question.models import Questionnaire


class QuestinnareResource(Resource):
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
                                   'description': mark.description} for mark in item.marks]
            datas.append(dict_item)
        return json_response(datas)

    @atomic
    @customer_required
    def post(self, request, *args, **kwargs):
        pass

    @atomic
    @customer_required
    def put(self, request, *args, **kwargs):
        pass
