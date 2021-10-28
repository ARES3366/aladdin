#!/usr/bin/env python
# -*- coding:utf-8 -*-
from exception_handler import ParamsException, InternalErrorException

def word_post(params):
    if not isinstance(params,dict):
        return {
            "status": 1,
            "message": "params was not dict"
        }
    if 'contents' not in params:
        return {
            "status": 1,
            "message": "'contents' was not in request.body"
        }
    contents =params['contents']
    cluster_num=1
    if "cluster_num" in params.keys():
        cluster_num = params["cluster_num"]
        if cluster_num==None:
            return_result={
                "status": 1,
                "message": "cluster_num None "
            }
            return return_result
        if not (isinstance(cluster_num, int)):
            return_result={
                "status": 1,
                "message": "the param 'cluster_num' was not int"
            }    
            return return_result
        if cluster_num <2 :
            return_result={
            "status": 1,
            "message": "Error cluster number "
            }
            return return_result

    if not (isinstance(contents, dict)):
        return_result={
            "status": 1,
            "message": "the param 'contents' was not a json dict"
        }    
        return return_result
    if len(contents)<10:
        return_result={
            "status": 1,
            "message": "The number of contents less than 10 "
        }
        return return_result
    if len(contents)>1000:
        return_result={
            "status": 1,
            "message": "The number of contents over 1000 "
        }
        return return_result
    for doc_name in contents.keys():
        if doc_name==None:
            return_result={
                "status": 1,
                "message": "Doc_name None "
            }
            return return_result
        if not (isinstance(doc_name, str)):
            return_result={
                "status": 1,
                "message": "One doc_name was not string"
            }
            return return_result
        if len(doc_name.strip())==0:
            return_result={
                "status": 1,
                "message": "Error doc_name "
            }
            return return_result
        if len(doc_name)>128:
            return_result={
                "status": 1,
                "message": "One doc_name length over 128"
            }
            return return_result
        ts=['\\',  '/', ':', ',', '*', '?', '"', '<', '>', '|']
        for t in ts:
            if t in doc_name:
                return_result={
                "status": 1,
                "message": "One doc_name contains special characters"
                }
                return return_result
        
        if 'content' not in contents[doc_name]:
            return_result={
                "status": 1,
                "message": "Doc has no content "
            }
            return return_result
        doc_content = contents[doc_name]['content']
        if doc_content==None:
            return_result={
                "status": 1,
                "message": "Doc has no content "
            }
            return return_result
        if not (isinstance(doc_content, str)):
            return_result={
                "status": 1,
                "message": "One doc_content was not string"
            }
            return return_result
        if len(doc_content.strip())==0:
            return_result={
                "status": 1,
                "message": "Content of {} was null ".format(doc_name)
            }
            return return_result
        
        if len(doc_content)>10000:
            doc_con=doc_content[:10000]
            contents[doc_name]['content']=doc_con
    if len(contents)<cluster_num:
        return_result={
            "status": 1,
            "message": "cluster_num more than the number of contents"
        }
        return return_result
    return {'status':0,'contents':contents,'cluster_num':cluster_num}

def word_put(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params  was not dict"
        }
        return return_result 
    if 'taskid' not in params or 'doc_name' not in params or 'action' not in params :
        return {
            "status": 1,
            "message": "Parameter missing"
        }
    taskid =params['taskid']
    if taskid==None:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was None"
        }
        return return_result
    if not (isinstance(taskid, str)):
        return_result={
            "status": 1,
            "message": "the param 'taskid' was not a string"
        }
        return return_result 
    if len(taskid.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was null"
        }
        return return_result
    doc_name =params['doc_name']
    if doc_name==None:
        return_result={
            "status": 1,
            "message": "the param 'doc_name' was None"
        }
        return return_result
    if not (isinstance(doc_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'doc_name' was not a string"
        }   
        return return_result
    if len(doc_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'doc-name' was null"
        }
        return return_result
    action =params['action']
    if action==None:
        return_result={
            "status": 1,
            "message": "the param 'action' was None"
        }
        return return_result
    if not (isinstance(action, int)):
        return_result={
            "status": 1,
            "message": "the param 'action' was not a int"
        }
        return return_result
    return {"status":0,"params":params}

def word_get_delete(taskid):
    if taskid == None:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was None"
        }
        return return_result
    if not (isinstance(taskid, str)):
        return_result={
            "status": 1,
            "message": "the param 'taskid' was not a string"
        }
        return return_result
    if len(taskid.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was null"
        }
        return return_result
    return {"status":0}

def condition_delete(cond_id):
    if cond_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was None"
        }
        return return_result
    if not (isinstance(cond_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was not a str"
        }
        return return_result
    if len(cond_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was null"
        }
        return return_result
    return {"status":0}

def condition_delete_docname(doc_name):  
    if not (isinstance(doc_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'doc_name' was not a str"
        }
        return return_result
    if len(doc_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'doc_name' was null"
        }
        return return_result
    return {"status":0}

def condition_get(cond_id):
    if not (isinstance(cond_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was not a string"
        }
        return return_result
    if len(cond_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was null"
        }
        return return_result
    return {"status":0}


def condition_post(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params was not dict"
        }
        return return_result
    if 'taskid' not in params or 'class_name' not in params or 'group_id' not in params or 'cond_name' not in params :
        return {
            "status": 1,
            "message": "Parameter missing"
        }
    taskid =params['taskid']
    if taskid ==None:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was None"
        }
        return return_result
    if not (isinstance(taskid, str)):
        return_result={
            "status": 1,
            "message": "the param 'taskid' was not a str"
        }
        return return_result 
    if len(taskid.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was null"
        }
        return return_result
    class_name =params['class_name']
    if class_name ==None:
        return_result={
            "status": 1,
            "message": "the param 'class_name' was None"
        }
        return return_result
    if not (isinstance(class_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'class_name' was not a str"
        }
        return return_result
    if len(class_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'class-name' was null"
        }
        return return_result
    group_id =params['group_id']
    if group_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was None"
        }
        return return_result
    if not (isinstance(group_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'group_id' was not a str"
        }
        return return_result  
    if len(group_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was null"
        }
        return return_result
    cond_name =params['cond_name']
    if cond_name ==None:
        return_result={
            "status": 1,
            "message": "the param 'cond_name' was None"
        }
        return return_result
    if not (isinstance(cond_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'cond_name' was not a str"
        }
        return return_result
    if len(cond_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'cond_name' was null"
        }
        return return_result
    if len(cond_name)>128:
        return_result={
            "status": 1,
            "message": "The param 'cond_name' length over 128"
        }
        return return_result
    ts=['\\',  '/', ':', ',', '*', '?', '"', '<', '>', '|']
    for t in ts:
        if t in cond_name:
            return_result={
            "status": 1,
            "message": "The param 'condi_name' contains special characters"
            }
            return return_result
    if len(cond_name.strip())<len(cond_name):
        params['cond_name']=cond_name.strip()
    
    return {"status":0,"params":params}

def condition_put(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params was not dict"
        }
        return return_result
    if 'cond_id' not in params:
        return {
            "status": 1,
            "message": "'cond_id' was not in request.body"
        }
    cond_id =params['cond_id']
    if cond_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was None"
        }
        return return_result
    if not (isinstance(cond_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was not a str"
        }
        return return_result
    if len(cond_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was null"
        }
        return return_result
    if 'cond_name' not in params:
        return {
            "status": 1,
            "message": "'cond_name' was not in request.body"
        }
    cond_name =params['cond_name']
    if cond_name ==None:
        return_result={
            "status": 1,
            "message": "the param 'cond_name' was None"
        }
        return return_result
    if not (isinstance(cond_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'cond_name' was not a str"
        }
        return return_result
    if len(cond_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'cond_name' was null"
        }
        return return_result
    if len(cond_name)>128:
        return_result={
            "status": 1,
            "message": "The param 'cond_name' length over 128"
        }
        return return_result
    ts=['\\',  '/', ':', ',', '*', '?', '"', '<', '>', '|']
    for t in ts:
        if t in cond_name:
            return_result={
            "status": 1,
            "message": "The param 'cond_name' contains special characters"
            }
            return return_result
    if len(cond_name.strip())<len(cond_name):
        params['cond_name']=cond_name.strip()
    return {"status": 0,"params":params}



def group_post(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params  was not dict"
        }
        return return_result 
    if 'group_name' not in params:    
        return {
            "status": 1,
            "message": "'group_name' was not in request body"
        }
    group_name =params['group_name']
    if group_name ==None:
        return_result={
            "status": 1,
            "message": "the param 'group_name' was None"
        }
        return return_result
    if not (isinstance(group_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'group_name' was not a str "
        }
        return return_result
    if len(group_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'group_name' was null"
        }
        return return_result
    if len(group_name)>128:
        return_result={
            "status": 1,
            "message": "The param 'group_name' length over 128"
        }
        return return_result
    ts=['\\',  '/', ':', ',', '*', '?', '"', '<', '>', '|']
    for t in ts:
        if t in group_name:
            return_result={
            "status": 1,
            "message": "The param 'group_name' contains special characters"
            }  
            return return_result
    if len(group_name.strip())<len(group_name):
        params['group_name']=group_name.strip()
    
    return {"status": 0,"params":params}

def group_put(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params  was not dict"
        }
        return return_result
    if 'group_id' not in params:
        return {
            "status": 1,
            "message": "'group_id' was not in request body"
        }
    group_id =params['group_id']
    if group_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was None"
        }
        return return_result
    if not (isinstance(group_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'group_id' was not a str"
        }
        return return_result
    if len(group_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was null"
        }
        return return_result
    if 'group_name' not in params:
        return {
            "status": 1,
            "message": "'group_name' was not in request body"
        }
    group_name =params['group_name']
    if group_name ==None:
        return_result={
            "status": 1,
            "message": "the param 'group_name' was None"
        }
        return return_result
    if not (isinstance(group_name, str)):
        return_result={
            "status": 1,
            "message": "the param 'group_name' was not a str"
        }
        return return_result
    if len(group_name.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'group_name' was null"
        }
        return return_result
    if len(group_name.strip())>128:
        return_result={
            "status": 1,
            "message": "The param 'group_name' length over 128"
        }
        return return_result
    ts=['\\',  '/', ':', ',', '*', '?', '"', '<', '>', '|']
    for t in ts:
        if t in group_name:
            return_result={
            "status": 1,
            "message": "The param 'group_name' contains special characters"
            }
            return return_result
    if len(group_name.strip())<len(group_name):
        params['group_name']=group_name.strip()
    return {"status":0,"params":params}

def group_get(group_id):
    if not (isinstance(group_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'group_id' was not a string"
        }
        return return_result
    if len(group_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was null"
        }
        return return_result
    return {"status":0}

def group_only_get(only):
    if only ==None:
        return_result={
            "status": 1,
            "message": "the param 'only' was None"
        }
        return return_result
    if not (isinstance(only, str)):
        return_result={
            "status": 1,
            "message": "the param 'only' was not string"
        }
        return return_result
    if only != '0' and only != '1':
        return_result={
            "status": 1,
            "message": "the param 'only' was not '0' or '1'"
        }
        return return_result
    return {"status":0}
def group_delete(group_id):
    if group_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was None"
        }
        return return_result
    if not (isinstance(group_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'group_id' was not a string"
        }
        return return_result
    if len(group_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'group_id' was null"
        }
        return return_result
    return {"status": 0}

def filter_params_check(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params  was not dict"
        }
        return return_result
    if 'content' not in params or 'condition' not in params :
        return {
            "status": 1,
            "message": "Parameter missing"
        }
    content =params['content']
    if content ==None:
        return_result={
            "status": 1,
            "message": "the param 'content' was None"
        }
        return return_result
    if not (isinstance(content, str)):
        return_result={
            "status": 1,
            "message": "the param 'content' was not a string"
        }
        return return_result
    if len(content.strip()) ==0:
        return_result={
            "status": 1,
            "message": "the param 'content' was null"
        }
        return return_result
    if len(content)>10000:
        doc_con=content[:10000]
        params['content']=doc_con
    condition =params['condition']
    if not (isinstance(condition, list)):
        return_result={
            "status": 1,
            "message": "the param 'condition' was not list"
        }
        return return_result
    if len(condition)>100:
        return_result={
            "status": 1,
            "message": "the num of condition over 100"
        }
        return return_result
    if len(condition)==0:
        return {"status":0,"params":params}
    for i in condition:
        if i ==None:
            return_result={
                "status": 1,
                "message": "the param 'cond_id' was None"
            }
            return return_result
        if not (isinstance(i, str)):
            return_result={
                "status": 1,
                "message": "the param 'cond_id' was not a string"
            }
            return return_result
        if len(i) ==0:
            return_result={
                "status": 1,
                "message": "the param 'cond_id' was null"
            }
            return return_result
    return {"status":0,"params":params}

def filter_analysis_check(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params  was not dict"
        }
        return return_result
    if 'content' not in params or 'condition' not in params or 'expect_cond_id' not in params:
        return {
            "status": 1,
            "message": "Parameter missing"
        }
    content =params['content']
    if content ==None:
        return_result={
            "status": 1,
            "message": "the param 'content' was None"
        }
        return return_result
    if not (isinstance(content, str)):
        return_result={
            "status": 1,
            "message": "the param 'content' was not a string"
        }
        return return_result
    if len(content.strip()) ==0:
        return_result={
            "status": 1,
            "message": "the param 'content' was null"
        }
        return return_result
    if len(content)>10000:
        doc_con=content[:10000]
        params['content']=doc_con
    expect_cond_id = params['expect_cond_id']
    if expect_cond_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'expect_cond_id' was None"
        }
        return return_result
    if not (isinstance(expect_cond_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'expect_cond_id' was not a string"
        }
        return return_result
    if len(expect_cond_id.strip()) ==0:
        return_result={
            "status": 1,
            "message": "the param 'expect_cond_id' was null"
        }
        return return_result
    condition =params['condition']
    if not (isinstance(condition, list)):
        return_result={
            "status": 1,
            "message": "the param 'condition' was not list"
        }
        return return_result
    if len(condition)>100:
        return_result={
            "status": 1,
            "message": "the num of condition over 100"
        }
        return return_result
    if len(condition)==0:
        return {"status":0,"params":params}
    for i in condition:
        if i ==None:
            return_result={
                "status": 1,
                "message": "the param 'cond_id' was None"
            }
            return return_result
        if not (isinstance(i, str)):
            return_result={
                "status": 1,
                "message": "the param 'cond_id' was not a string"
            }
            return return_result
        if len(i.strip()) ==0:
            return_result={
                "status": 1,
                "message": "the param 'cond_id' was null"
            }
            return return_result
    return {"status":0,"params":params}


def conditionAssign_post(params):
    if not (isinstance(params, dict)):
        return_result={
            "status": 1,
            "message": "the params was not dict"
        }
        return return_result
    if 'taskid' not in params or 'file_list' not in params or 'cond_id' not in params  :
        return {
            "status": 1,
            "message": "Parameter missing"
        }
    taskid =params['taskid']
    if taskid ==None:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was None"
        }
        return return_result
    if not (isinstance(taskid, str)):
        return_result={
            "status": 1,
            "message": "the param 'taskid' was not a str"
        }
        return return_result 
    if len(taskid.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'taskid' was null"
        }
        return return_result
    cond_id =params['cond_id']
    if cond_id ==None:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was None"
        }
        return return_result
    if not (isinstance(cond_id, str)):
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was not a str"
        }
        return return_result
    if len(cond_id.strip())==0:
        return_result={
            "status": 1,
            "message": "the param 'cond_id' was null"
        }
        return return_result
    
    file_list=params['file_list']
    if not (isinstance(file_list, list)):
        return_result={
            "status": 1,
            "message": "the param 'file_list' was not a list"
        }
        return return_result  
    if len(file_list)==0:
        return_result={
            "status": 1,
            "message": "the param 'file_list' have no file"
        }
        return return_result
    for f in file_list:
        if f ==None:
            return_result={
                "status": 1,
                "message": "one file name was None"
            }
            return return_result
        if not (isinstance(f, str)):
            return_result={
                "status": 1,
                "message": "one file name was not a str"
            }
            return return_result
        if len(f.strip())==0:
            return_result={
                "status": 1,
                "message": "one file name was null"
            }
            return return_result
    
    return {"status":0,"params":params}