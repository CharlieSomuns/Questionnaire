import json
import os
from datetime import datetime

from django.db.transaction import atomic

from Api.resources import Resource
from Api.utils import *
from Api.decoretors import *


class QuestinnareResource(Resource):

    @atomic
    @customer_required
    def post(self, request, *args, **kwargs):
        pass

    @atomic
    @customer_required
    def put(self, request, *args, **kwargs):
        pass
