# -*- coding: utf-8 -*-
import json
#import time
import os
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))


def store(data):
    with open(_get_module_path('property/default.json'), 'w') as json_file:
        json_file.write(json.dumps(data))

def load():
    with open(_get_module_path('property/default.json'),'r') as json_file:
        data = json.load(json_file)
        list_class = []
        defalut_class = data["default"]["default_classes"]
        if defalut_class["cn_passport"]=="true":
            list_class.append('cn_passport')
        if defalut_class["cn_telephone"] == "true":
            list_class.append('cn_telephone')
        if defalut_class["cn_email"] == "true":
            list_class.append('cn_email')
        if defalut_class["cn_bank"] == "true":
            list_class.append('cn_bank')
        if defalut_class["cn_date"] == "true":
            list_class.append('cn_date')
        if defalut_class["cn_id"] == "true":
            list_class.append('cn_id')
        return list_class

def update(_default,num,rate_grade):
    default={}
    default["limit"] = num
    default["rate_grade"] = rate_grade
    default["default_classes"] = _default
    data = {}
    data["default"] = default
    store(data)
    return load()
def update_default_property(param):
    if param['recognize_class'] =='update':
        return update(param['update_propertiy'],300,param['rate_grade'])
    if param['recognize_class'] =='check':
        return load()
    if param['recognize_class'] =='default':
        defaule_classes = {}
        defaule_classes["cn_id"] = "true"
        defaule_classes["cn_bank"] = "true"
        defaule_classes["cn_email"] = "true"
        defaule_classes["cn_date"] = "false"
        defaule_classes["cn_telephone"] = "true"
        defaule_classes["cn_passport"] = "false"

        return update(defaule_classes,300,"中")






