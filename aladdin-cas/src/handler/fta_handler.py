#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import json
import tornado.web

# from analysis_package.text_spectral_cluster import spectral_cluster
# from analysis_package.operate_atf_db import  clusterResultGet,docsWordsPut,condiGroupGet,docsWordsDelete,condiGroupPost,condiGroupPut,condiGroupDelete,conditionPut,conditionPost,conditionGet,conditionDelete,condidocsDelete
# from analysis_package.sensitive_text_tag import sensitive_tag
from fta.do_fta import fastTextAnalysis,fta_keywords
from fta.fta_params_check import fta_post_parmas,fta_keyword_params
import numpy as np

class FtaHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        try:
            return_result = {
                "status": 1
            }
            params = json.loads(self.request.body.decode())
            result = fta_post_parmas(params)  
            if result['status'] == 1:
                self.set_status(400)
                return self.write(result)
            params = result['params']
            data = fastTextAnalysis(params)          
            return_result={
                "status": 0,
                "data": data
            }
            self.set_status(200)
            return self.write(return_result)            
        except Exception as e:
            return_result = {
                "status": 1,
            }
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class FtaKeywordsHandler(tornado.web.RequestHandler):   
    async def post(self, *args, **kwargs):
        try:
            return_result = {
                "status": 1
            }
            params = json.loads(self.request.body.decode())
            result = fta_keyword_params(params)
            if result['status'] == 1:
                self.set_status(400)
                return self.write(result) 
            params = result['params']      
            if len(params['content']) == 0:
                return_result={
                    "status": 0,
                     "keywords": []
                }
                self.set_status(200)
                return self.write(return_result)                   
            data = fta_keywords(params)          
            return_result={
                "status": 0,
                "keywords": data
            }
            self.set_status(200)
            return self.write(return_result)           
        except Exception as e:
            return_result = {
                "status": 1,
            }
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)
