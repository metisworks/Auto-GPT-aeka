from mongoengine import connect, disconnect
from mongo_cache.models.result_object import ResultObject
import uuid


class ResultObjDbOperation(object):
    _instance = None

    def __init__(self, connection_string=None, db_name=None):
        super().__init__()

    def __new__(cls, db_connection_string=None, db_name=None):
        if cls._instance is None:
            if not db_connection_string:
                raise Exception(" db_connection_string not given")
            if not db_name:
                raise Exception(" db_name not given")
            print('Creating the object')
            cls._instance = super().__new__(cls)
            cls._instance.connection_string = db_connection_string
            cls._instance.db_name = db_name
            cls._instance.connected = None
            cls._instance.id = str(uuid.uuid4())
        return cls._instance

    def create_connection(self):
        if self.connected is None:
            self.connected = connect(
                self.db_name,
                host=self.connection_string,
                alias="default"
            )
            print(f"New Connection for id {self.id}..{self.connected}")
        print(f" Using existing connection object: {str(self.id)}")

    def _terminate_connection(self):
        if self.connected is not None:
            disconnect("default")
        self.connected = None

    def get_result_obj(self, run_id) -> ResultObject:
        self.create_connection()
        res_obj = ResultObject.objects(run_id=run_id).first()
        if res_obj:
            res_obj.retrieval_count += 1
            res_obj.save()
        return res_obj

    def add_result_obj(self, run_id, input_goals: dict, result: dict) -> None:
        res_obj = ResultObject()
        res_obj.run_id = run_id
        res_obj.results = {"result_value": result}
        res_obj.retrieval_count = 0
        res_obj.input_goals = input_goals
        self.create_connection()
        res_obj.save()
        return


def get_result_db_operations():
    return


if __name__ == "__main__":
    ro1 = ResultObjDbOperation("mongodb+srv://metisadmin:metisdata2023@cluster1.616znwm.mongodb.net/", "metis")
    print(f"{ ro1.id = }")

    RO2 = ResultObjDbOperation()
    print(f"{ RO2.id = }")
    print(f"{ RO2.connection_string = }")

    RO3 = ResultObjDbOperation()
    print(f"{ RO3.id = }")
    print(f"{ RO3.connection_string = }")
