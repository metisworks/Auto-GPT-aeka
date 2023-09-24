from mongo_cache.result_obj_db_operations import ResultObjDbOperation


def get_db():
    connection_string = "mongodb+srv://metisadmin:metisdata2023@cluster1.616znwm.mongodb.net/"
    db_name = "metis"
    return ResultObjDbOperation(connection_string=connection_string, db_name=db_name)
