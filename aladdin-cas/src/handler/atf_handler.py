#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import json
import tornado.web
import logging
from auto_text_filter.text_spectral_cluster import spectral_cluster
from auto_text_filter.operate_atf_db import  clusterResultGet,docsWordsPut,condiGroupGet,groupGet,docsWordsDelete,condiGroupPost,condiGroupPut,condiGroupDelete,conditionPut,conditionPost,conditionGet,conditionDelete,condidocsDelete,conditionAssignPost
from auto_text_filter.text_filter import text_filter_,filter_analysis,text_multi_filter_,multi_analysis

# import numpy as np
# import read_config
import uuid
# import multiprocessing
from auto_text_filter.atf_params_check import word_post,word_put,word_get_delete,condition_delete,condition_delete_docname,condition_get, condition_post,condition_put,group_get,group_only_get,group_delete, group_post,group_put,filter_params_check,filter_analysis_check,conditionAssign_post

from exception_handler import BasicException
from exception_handler import ParamsException, InternalErrorException


#参数判断结果为错时，封装返回结果
def check_paramsresult(s,result,ercode):
    cause = result['message']
    error_detail = {
        "parameters":result['message']
    }
    exception = ParamsException(cause=cause, detail = error_detail, error_code=ercode)
    s.set_status(int(exception.status_code))
    logging.warning(exception.generate_response())
    return exception.generate_response()
#内部函数执行错误时，封装返回结果
def check_interresult(s,return_result,ercode):
    cause = return_result['message']
    error_detail = {
        "traceback":traceback.format_exc()
    }
    return_err = InternalErrorException(cause=cause, detail=error_detail, error_code=ercode)
    s.set_status(int(return_err.status_code))
    logging.warning(return_err.generate_response())
    return return_err.generate_response()
#异常报错时封装错误返回结果
def check_exception(s,e,ercode):
    cause = e
    error_detail = {
        "traceback":traceback.format_exc()
    }
    return_err = InternalErrorException(cause=cause, detail=error_detail, error_code=ercode)
    s.set_status(int(return_err.status_code))
    logging.warning(return_err.generate_response())
    return return_err.generate_response()


class ATFWordHandler(tornado.web.RequestHandler):
    # def run_return_id(self, res):
    #     return self.write(res) 
    
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            result = word_post(params)
            if result['status']==1:
                return self.write(check_paramsresult(self,result=result,ercode='000'))
            contents = result['contents']
            cluster_num = result['cluster_num']
            taskid =str(uuid.uuid1())    
            return_result = spectral_cluster(contents,taskid,cluster_num)
            if return_result['status']==1:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)      
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
   
    async def get(self, *args, **kwargs):
        try:
            taskid = self.get_query_argument("taskid", None)
            result = word_get_delete(taskid)
            if result['status']==1:
                return self.write(check_paramsresult(self,result,'000'))
            return_result = await clusterResultGet(taskid)
            if return_result['status'] != 0:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

    async def put(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = word_put(params)
            if result["status"]==1:
                return self.write(check_paramsresult(self,result,'000'))
            params=result['params']
            return_result = await docsWordsPut(params['taskid'],params['doc_name'],params['action'])
            if return_result['status'] != 0:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
    async def delete(self, *args, **kwargs):
        try:
            taskid = self.get_query_argument("taskid", None)
            result = word_get_delete(taskid)
            if result['status'] == 1:
                return self.write(check_paramsresult(self,result,'000'))         
            return_result = await docsWordsDelete(taskid)
            if return_result['status'] != 0:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFGroupHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        try:
            # import pdb;pdb.set_trace()
            only = self.get_query_argument("only", None)
            result = group_only_get(only)
            if result['status'] !=0:
                return self.write(check_paramsresult(self,result,'000'))
            group_id = self.get_query_argument("group_id", None)
            if group_id ==None:
                if only=='0':
                    return_result = await groupGet()
                if only=='1':
                    return_result = await condiGroupGet()
                if return_result['status'] != 0:
                    return self.write(check_interresult(self,return_result,'000'))
                del return_result['status']
                return self.write(return_result)
            result = group_get(group_id)
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            if only=='0':
                return_result = await groupGet(group_id=group_id)
            if only=='1':
                return_result = await condiGroupGet(group_id=group_id)
            if return_result['status'] != 0:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
            
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = group_post(params)   
            if result['status'] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            params=result["params"]
            return_result = await condiGroupPost(params['group_name'])
            if return_result['status']==1:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status'] 
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
    async def delete(self, *args, **kwargs):
        try:
            group_id = self.get_query_argument("group_id", None)  
            result = group_delete(group_id) 
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000')) 
            return_result = await condiGroupDelete(group_id)
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            if return_result['status']==2:
                return self.write(check_interresult(self,return_result,'001'))
            del return_result['status'] 
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
    async def put(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = group_put(params)
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            params=result["params"]
            return_result = await condiGroupPut(params['group_id'],params['group_name'])
            if return_result['status']==1:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status'] 
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFConditionHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        try:
            cond_id = self.get_query_argument("cond_id", None)   
            if cond_id ==None:
                return_result = await conditionGet()
                if return_result['status'] != 0:
                    return self.write(check_interresult(self,return_result,'000'))
                del return_result['status']  
                return self.write(return_result)
            result = condition_get(cond_id)
            if result["status"]==1:
                return self.write(check_paramsresult(self,result,'000'))
            return_result = await conditionGet(cond_id=cond_id)
            if return_result['status'] != 0:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = condition_post(params)
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            params=result["params"]
            return_result = await conditionPost(params['taskid'],params['class_name'],params['group_id'],params['cond_name'])
            if return_result['status']==1:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status'] 
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
    async def delete(self, *args, **kwargs):
        try: 
            cond_id = self.get_query_argument("cond_id", None)
            doc_name = self.get_query_argument("doc_name", None)
            result =condition_delete(cond_id) 
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            if doc_name == None:
                return_result = await conditionDelete(cond_id)
                if return_result['status']==1:
                    return self.write(check_interresult(self,return_result,'000'))
                if return_result['status']==2:
                    return self.write(check_interresult(self,return_result,'001'))
                del return_result['status']
                return self.write(return_result) 
            result = condition_delete_docname(doc_name) 
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            return_result = await condidocsDelete(cond_id,doc_name)
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            if return_result['status']==2:
                return self.write(check_interresult(self,return_result,'001'))
            del return_result['status']
            return self.write(return_result) 
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))
    async def put(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = condition_put(params)
            if result["status"] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            params = result['params']
            return_result = await conditionPut(params['cond_id'],params['cond_name'])
            if return_result['status']==1:
                return self.write(check_interresult(self,return_result,'000'))
            del return_result['status'] 
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFFilterHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = filter_params_check(params)
            if result['status'] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            params = result['params']   
            return_result = await text_filter_(params['content'],params['condition'])
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            if return_result['status']==2:
                return self.write(check_interresult(self,return_result,'001'))
            del return_result['status']

            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFFilterAnalysisHandler(tornado.web.RequestHandler):
    async def post(self,*args,**kwargs):
        try:
            params = json.loads(self.request.body.decode())
            result = filter_analysis_check(params)
            if result['status']==1:
                return self.write(check_paramsresult(self,result,'000'))
            params =result['params']
            return_result = await filter_analysis(params['content'],params['condition'],params['expect_cond_id'])
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            if return_result['status']==2:
                return self.write(check_interresult(self,return_result,'001'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFMultiFilterHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            result = filter_params_check(params)
            if result['status'] == 1:
                return self.write(check_paramsresult(self,result,'000'))
            params = result['params']   
            return_result = await text_multi_filter_(params['content'],params['condition'])
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            if return_result['status']==2:
                return self.write(check_interresult(self,return_result,'001'))
            del return_result['status']
            # return_re={}
            # return_re['classify_result'] = return_result
            # return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFMultiAnalysisHandler(tornado.web.RequestHandler):
    async def post(self,*args,**kwargs):
        try:
            params = json.loads(self.request.body.decode())
            result = filter_analysis_check(params)
            if result['status']==1:
                return self.write(check_paramsresult(self,result,'000'))
            params =result['params']
            return_result = await multi_analysis(params['content'],params['condition'],params['expect_cond_id'])
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            if return_result['status']==2:
                return self.write(check_interresult(self,return_result,'001'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

class ATFAssignConditonHandler(tornado.web.RequestHandler):
    async def post(self,*args,**kwargs):
        try:
            params = json.loads(self.request.body.decode())
            result = conditionAssign_post(params)
            if result['status']==1:
                return self.write(check_paramsresult(self,result,'000'))
            params =result['params']
            #taskid,file_list,cond_id,cond_name,group_id
            #'taskid'  'file_list' 'cond_id' 'group_id'  'cond_name' 
            return_result = await conditionAssignPost(params['taskid'],params['file_list'],params['cond_id'])
            if return_result['status']==1:
               return self.write(check_interresult(self,return_result,'000'))
            del return_result['status']
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return self.write(check_exception(self,e,'000'))

