#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import json
import tornado.web
from analysis_package.extract_method import extract_keywords, extract_abstract,  extract_keywords_abstract
from analysis_package.analysis_content import  match_keywords
from analysis_package.sensitive_dict import SensitiveDict
from analysis_package.doc_fingerprint import Simhash
from analysis_package.doc_fingerprint_search import Search
from analysis_package.doc_fingerprint_cluster import DocFingerprintCluster

from privacy_information_identity.identify_privacy_information import identity
from privacy_information_identity.update_default import update_default_property

from analysis_package.abstract_from_text_interception import get_abstract_from_text_interception
import numpy as np
from mess_utils.nlp_server import NlpServer
# from client.tfs_client import BaseClient
from acam_dict import WordTree
import read_config
import uuid
import multiprocessing

class PandoraBaseHandler(tornado.web.RequestHandler):
    overstock_body_len = 0
    # 由于tornado 获取post json 参数有问题， 于是新建自己的获取参数方法
    def get_json_argument(self, name, default=None):
        args = json.loads(self.request.body)

        # name = to_unicode(name)
        if name in args:
            return args[name]
        elif default is not None:
            return default
        else:
            raise Exception

    def get_pandora_argument(self, key, default):
        try:
            value = self.get_argument(key, default)
            if value is None:
                value = self.get_json_argument(key)
            return value
        except:
            return default

    def __init__(
        self,
        application: "Application",
        request ,
        **kwargs
    ) -> None:
        super(PandoraBaseHandler,self).__init__(application, request, **kwargs)
        self.json_params = {}

    def prepare(self):
        #检查累积的未处理请求的大小
        body_len = len(self.request.body)
        PandoraBaseHandler.overstock_body_len += body_len
        if PandoraBaseHandler.overstock_body_len > read_config.max_stock_body_size:
            self.set_status(400)
            self.write({
                "status": 2,
                "message": "overstock"
            })
            return self.finish()
        #检查公共参数是否合法
        try:
            params = json.loads(self.request.body.decode())
        except:
            self.set_status(400)
            self.write({
                "status": 3,
                "message": "param-type was not json"
            })
            return self.finish()
        if ('content' not in params) and ('content_list' not in params):
            self.set_status(400)
            self.write({
                "status": 4,
                "message": "'content' was not in json params"
            })
            return self.finish()
        
        if 'content' in params:    
            content = params['content']
            if not isinstance(content, str):
                self.set_status(400)
                self.write({
                    "status": 1,
                    "message": "'content' was no-string"
                })
                return self.finish()
            if len(content) > read_config.max_content_len:
                self.set_status(400)
                self.write({
                    "status": 5,
                    "message": "content length is too bigger"
                })
                return self.finish()

        if 'content_list' in params:    
            content_list = params['content_list']
            if not isinstance(content_list, list):
                self.set_status(400)
                self.write({
                    "status": 1,
                    "message": "'content_list' was not list"
                })
                return self.finish()
            for idx in range(len(content_list)):
                content = content_list[idx]
                if not isinstance(content, str):
                    self.set_status(400)
                    self.write({
                        "status": 1,
                        "message": "content_list[%s] was no-string"%idx
                    })
                    return self.finish()
                if len(content) > read_config.max_content_len:
                    self.set_status(400)
                    self.write({
                        "status": 5,
                        "message": "content length is too bigger, content_id is: %s"%idx
                    })
                    return self.finish()

        self.json_params = params

    def finish(self):
        body_len = len(self.request.body)
        PandoraBaseHandler.overstock_body_len -= body_len
        super(PandoraBaseHandler, self).finish()

class IllegalityHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1,
        }
        try:
            content = self.json_params['content']
            #content_len = len(content)
            class_name_list = ['legal','political','sexy','other_illegal']
            if not SensitiveDict().has_sensitive_word(content):
                label = [1, 0, 0, 0]
                return_result = {
                   "status": 0,
                   "class_name": class_name_list[0],
                   "probe_dist": {class_name_list[i]:round(float(label[i]),4) for i in range(len(label))}
                }
                return self.write(return_result)
            label = await NlpServer().async_predict(content,1)
            class_id = int(np.argmax(label))
            return_result = {
               "status": 0,
               "class_name": class_name_list[class_id],
               "probe_dist": {class_name_list[i]:round(float(label[i]),4) for i in range(len(label))}
            }
            self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.write(return_result)

class SensitivityHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1,
        }
        try:
            content = self.json_params['content']
            #content_len = len(content)
            words = self.json_params["words"]
            if not (isinstance(words, list)):
                return_result={
                    "status": 1,
                    "message": "the param 'words' was not a json list"
                }
                self.set_status(400)
                return self.write(return_result)    
            if len(words) == 0:
                return_result={
                    "status": 1,
                    "message": "words list length is 0"
                }
                self.set_status(400)
                return self.write(return_result)    
            if len(words) > 10000:
                return_result={
                    "status": 1,
                    "message": "words list length is bigger than 10000"
                }
                self.set_status(400)
                return self.write(return_result)
                
            for w in words:
                if not isinstance(w,str):
                    return_result={
                        "status": 1,
                        "message": "words have no-string element"
                    }
                    self.set_status(400)
                    return self.write(return_result)

                if len(w)>100:
                    return_result={
                        "status": 1,
                        "message": "word lenth is bigger than 100, error word is %s"%w,
                    }
                    self.set_status(400)
                    return self.write(return_result)

            return_result['word_loc'] = match_keywords(content,words)
            return_result['status'] = 0
            return self.write(return_result) 
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class BatchSensitivityHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1,
        }
        try:
            content_list = self.json_params['content_list']
            words = self.json_params["words"]
            if not (isinstance(self.json_params['words'], list)):
                return_result={
                    "status": 1,
                    "message": "the param 'words' was not a json list"
                }
                self.set_status(400)
                return self.write(return_result)    
            if len(words) == 0:
                return_result={
                    "status": 1,
                    "message": "words list length is 0"
                }
                self.set_status(400)
                return self.write(return_result)    
            if len(words) > 10000:
                return_result={
                    "status": 1,
                    "message": "words list length is bigger than 10000"
                }
                self.set_status(400)
                return self.write(return_result)
                
            for w in words:
                if not isinstance(w,str):
                    return_result={
                        "status": 1,
                        "message": "words have no-string element"
                    }
                    self.set_status(400)
                    return self.write(return_result)

                if len(w)>100:
                    return_result={
                        "status": 1,
                        "message": "word lenth is bigger than 100, error word is %s"%w,
                    }
                    self.set_status(400)
                    return self.write(return_result)

            tree = WordTree(filter_set={})#{"*", "?", "$", "#", "@", "!", " "})
            tree.build(words)
            word_locate_list = [dict() for i in range(len(content_list))]
            for cid in range(len(content_list)):
                content = content_list[cid]
                #content_len = len(content)
                #r, _ = tree.search_multi(content)
                word_locate_list[cid] = match_keywords(content, words, tree)
            return_result['word_loc'] = word_locate_list
            return_result['status'] = 0
            return self.write(return_result) 
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class ExtractKeywordsHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            top_num = self.json_params['top_num']
            if not isinstance(top_num, int):
                return_result = {
                    "status":1,
                    "message":"top_num was not integer type " 
                }
                self.set_status(400)
                return self.write(return_result)
            if top_num not in range(101):
                return_result = {
                    "status":1,
                    "message":"top_num not in range [0, 100]" 
                }
                self.set_status(400)
                return self.write(return_result)
            return_result['keywords'] = extract_keywords(content, top_num, level=2)
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            self.write(return_result)

class ExtractAbstractHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            content_len = len(content)
            max_abstract_content_length = 4*2**20
            if content_len > 4*2**20:
                content = content[0:max_abstract_content_length]
            return_result['abstract'] = extract_abstract(content)
            return_result['status'] = 0
            return self.write(return_result)        
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class ExtractAbstractFromTextInterceptionHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            content_len = len(content)
            max_abstract_content_length = 4*2**20
            if content_len > 4*2**20:
                content = content[0:max_abstract_content_length]
            return_result['abstract'] = get_abstract_from_text_interception(content)
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class ExtractHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            content_len = len(content)
            top_num = self.json_params['top_num']
            if not isinstance(top_num, int):
                return_result = {
                    "status":1,
                    "message":"top_num was not integer type " 
                }
                self.set_status(400)
                return self.write(return_result)
            if top_num not in range(101):
                return_result = {
                    "status":1,
                    "message":"top_num not in range [0, 100]" 
                }
                self.set_status(400)
                return self.write(return_result)
            max_abstract_content_length = 4*2**20
            if content_len > 4*2**20:
                content = content[0:max_abstract_content_length]
            return_result['keywords'], return_result['abstract'] = extract_keywords_abstract(content, top_num)
            return_result['status'] = 0
            return self.write(return_result)        
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class PrivacyRecognizeHandler(PandoraBaseHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            # top_num = self.json_params['top_num']
            if not isinstance(content, str):
                return_result = {
                    "status":1,
                    "message":"cotent was not str type "
                }
                self.set_status(400)
                return self.write(return_result)
            
            result= await identity.get_properties(content)
            return_result['num'] = result['num']
            return_result['message'] = result['message']
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            self.write(return_result)

class PrivacyProperytHandler(tornado.web.RequestHandler):
    def put(self, *args, **kwargs):
        try:
            return_result = {
                "status": 1
            }
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            if 'parameter' not in params:
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'parameter' was not in request.body"
                })
            parameter = params['parameter']
            if not isinstance(parameter,dict):
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'parameter' was no-dic"
                })
            rate_grade=parameter["rate_grade"]
            if not isinstance(rate_grade,str):
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'rate_grade' was no-string"
                })
            recognize_class=parameter["recognize_class"]
            if not isinstance(recognize_class,str):
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'recognize_class' was no-string"
                })
            if recognize_class not in ["update","check","default"]:
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "error parameter"
                })
            if recognize_class=='update':
                if 'update_propertiy' not in parameter:
                    self.set_status(400)
                    return self.write({
                        "status": 1,
                        "message": "has no 'update_property'"
                    })

                update_propertity = parameter['update_propertiy']
                if not isinstance(update_propertity,dict):
                    self.set_status(400)
                    return self.write({
                        "status": 1,
                        "message": "'update_propertity' was no-dict"
                    })
                for ke in update_propertity:
                    if not isinstance(ke,str):
                        self.set_status(400)
                        return self.write({
                            "status": 1,
                            "message": "'key' was no-string"
                        })
                    valu = update_propertity[ke]
                    if not isinstance(valu,str):
                        self.set_status(400)
                        return self.write({
                            "status": 1,
                            "message": "'value' was no-string"
                        })
                    if valu not in ["true","false"]:
                        self.set_status(400)
                        return self.write({
                            "status": 1,
                            "message": "error parameter"
                        })
            result = update_default_property(parameter)
            return_result['class_message'] = result
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"] = str(e)
            self.set_status(400)
            return self.write(return_result)
class ExtractDocFingerPrintHandler(PandoraBaseHandler):
   
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            content_len = len(content)
            if content_len>1*2**20:
                return_result={
                    "status": 1,
                    "message": "the text is more than 1M length "
                }
                self.set_status(400)
                return self.write(return_result)
            if content_len==0:
                return_result['docufingerprint'] = "" 
                return_result['status'] = 0
                return self.write(return_result)
            sh=Simhash()
            return_result['docufingerprint'] = sh.simhash(content)
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)
class ExtractFingerPrintKeywordsHandler(PandoraBaseHandler):

    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1
        }
        try:
            content = self.json_params['content']
            content_len = len(content)
            if content_len>1*2**20:
                return_result={
                    "status": 1,
                    "message": "the text is more than 1M length "
                }
                self.set_status(400)
                return self.write(return_result)
            if content_len==0:
                return_result['fingerprint_keywords'] = []
                return_result['status'] = 0
                return self.write(return_result)
            sh=Simhash()
            return_result['fingerprint_keywords'] = sh.keywords(content)
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()

            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)

class SearchDocumentHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        try:
            return_result = {
                "status": 1
            }
            params = json.loads(self.request.body.decode())
            #self.json_params = params
            if 'fingerprint' not in params:
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'fingerprint' was not in request.body"
                })
            fingerprint =params['fingerprint']
            if not (isinstance(fingerprint, dict)):
                return_result={
                    "status": 1,
                    "message": "the param 'fingerprint' was not a json dict"
                }
                self.set_status(400)
                return self.write(return_result)
            if 'target_doc' not in fingerprint.keys():
                return_result={
                    "status": 1,
                    "message": "the param has no 'target_doc' "
                }
                self.set_status(400)
                return self.write(return_result)
        
            if 'fingerprint_db' not in fingerprint.keys():
                return_result={
                    "status": 1,
                    "message": "the param has no 'fingerprint_db'"
                }
                self.set_status(400)
                return self.write(return_result)
            target_doc = fingerprint['target_doc']
            fingerprint_db = fingerprint['fingerprint_db']
            if not (isinstance(target_doc,dict)):
                return_result={
                    "status": 1,
                    "message": "the param 'target_doc' was not a json dict"
                }
                self.set_status(400)
                return self.write(return_result)
            if not (isinstance(fingerprint_db,dict)):
                return_result={
                    "status": 1,
                    "message": "the param 'fingerprint_db' was not a json dict"
                }
                self.set_status(400)
                return self.write(return_result)
            sc=Search() 
            search_message = sc.search_doc(fingerprint)
            return_result['search_message'] =search_message 
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)
class ExtractDocFingerPrintClusterHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        try:
            return_result = {
                "status": 1
            }
            params = json.loads(self.request.body.decode())
            if 'fingerprints' not in params:
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'fingerprint' was not in request.body"
                })
            if 'grad' not in params:
                self.set_status(400)
                return self.write({
                    "status": 1,
                    "message": "'grad' was not in request.body"
                })
            fingerprint =params['fingerprints']
            if not (isinstance(fingerprint, dict)):
                return_result={
                    "status": 1,
                    "message": "the param 'fingerprint' was not a json dict"
                }
                self.set_status(400)
                return self.write(return_result)
            grad = params['grad']
            if isinstance(grad, bool):
                return_result={
                    "status": 1,
                    "message": "the param 'grad' cannot be a bool"
                }
                self.set_status(400)
                return self.write(return_result)
            if not (isinstance(grad, int)):
                return_result={
                    "status": 1,
                    "message": "the param 'grad' was not int"
                }
                self.set_status(400)
                return self.write(return_result)
            if grad<2 or grad >= 6:
                return_result={
                    "status": 1,
                    "message": "the range of param 'grad' was error"
                }
                self.set_status(400)
                return self.write(return_result)
            if len(fingerprint)==0:
                search_message = []
                return_result['similardocs_set'] =search_message
                return_result['status'] = 0
                return self.write(return_result)
            for k,v in fingerprint.items():
                if not (isinstance(k, str)):
                    return_result={
                        "status": 1,
                        "message": "one doc name of param 'fingerprints' was not str"
                    }
                    self.set_status(400)
                    return self.write(return_result)
                if len(k.strip())==0:
                    return_result={
                        "status": 1,
                        "message": "one doc name of param 'fingerprints' was none"
                    }
                    self.set_status(400)
                    return self.write(return_result)
                if not (isinstance(v, str)):
                    return_result={
                        "status": 1,
                        "message": "one doc fingerprint of 'fingerprints' was not str"
                    }
                    self.set_status(400)
                    return self.write(return_result)
                if not v.isdigit():
                    return_result={
                        "status": 1,
                        "message": "one doc fingerprint of 'fingerprints' was not pure digital"
                    }
                    self.set_status(400)
                    return self.write(return_result)
            if len(fingerprint)==1:
                search_message = []
                search_message.append(list(fingerprint.keys()))
                return_result['similardocs_set'] =search_message
                return_result['status'] = 0
                return self.write(return_result)
            dfc = DocFingerprintCluster(fingerprint,grad)          
            search_message = dfc.cluster()
            return_result['similardocs_set'] =search_message
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            return_result["message"]=str(e)
            self.set_status(400)
            return self.write(return_result)
