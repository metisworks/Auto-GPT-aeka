from mongoengine import *


class ResultObject(DynamicDocument):
    run_id = StringField(required=True)
    retrieval_count = IntField(required=True, default=0)
    input_goals = DictField(required=True)
    results = DictField()

