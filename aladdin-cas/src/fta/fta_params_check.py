#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import json


def fta_post_parmas(params):
    if 'content' not in params:
        return {
            "status": 1,
            "message": "'contents' was not in request.body"
        }
    content =params['content']
    if 'action' not in params:
        return {
            "status": 1,
            "message": "'action' was not in request.body"
        }
    action = params['action']
    if not (isinstance(content, str)):
        return_result={
            "status": 1,
            "message": "content was not string"
        }      
        return return_result

    if len(content)==0:
        return_result={
            "status": 1,
            "message": "No content "
        }     
        return return_result
    if len(content)>10000:
        content=content[:10000]
        params['content']=content 
    if not (isinstance(action, dict)):
        return_result={
            "status": 1,
            "message": "action was not dict"
        }
        return return_result
    if len(action)==0:
        return_result={
            "status": 1,
            "message": "No action "
        }
        return return_result
    
    if 'keywords' in action.keys():
        if 'top_num' not in action['keywords'].keys() or "keyphrase" not in action['keywords'].keys():
            return_result={
                "status": 1,
                "message": " Error params "
            }
            return return_result
        top_num = action['keywords']['top_num']
        if isinstance(top_num, bool):
            return_result={
                "status": 1,
                "message": "Param 'top_num' cannot be a bool"
            }
            return return_result
        if not (isinstance(top_num, int)):
            return_result={
                "status": 1,
                "message": "Error param 'top_num'"
            }
            return return_result
        if top_num<=0 or top_num>100:
            return_result={
                "status": 1,
                "message": "Error param 'top_num'"
            }
            return return_result
        keyphrase = action['keywords']['keyphrase']
        if not (isinstance(keyphrase, bool)):
            return_result={
                "status": 1,
                "message": "Error param 'keyphrase'"
            }
            return return_result
    if 'abstract' in action.keys():
        
        abstract = action['abstract']
        if not (isinstance(abstract, bool)):
            return_result={
                "status": 1,
                "message": "Error param 'abstract'"
            }
            return return_result
    if 'fingerprint' in action.keys():       
        fingerprint = action['fingerprint']
        if not (isinstance(fingerprint, bool)):
            return_result={
                "status": 1,
                "message": "Error param 'fingerprint'"
            }
            return return_result
    if 'common_class' in action.keys():             
        common_class = action['common_class']
        if not (isinstance(common_class, bool)):
            return_result={
                "status": 1,
                "message": "Error param 'common_class'"
            }
            return return_result
    return {'status':0,'params':params}

def fta_keyword_params(params):
    if 'content' not in params:
        return {
            "status": 1,
            "message": "'contents' was not in request.body"
        }
    content =params['content']
    if not (isinstance(content, str)):
        return_result={
            "status": 1,
            "message": "content was not string"
        }
        return return_result
    # if len(content)==0:
    #     return_result={
    #         "status": 0,
    #             "keywords": []
    #     }
    #     return return_result       
    if len(content)>10000:
        content=content[:10000]
        params['content']=content
    return {'status':0,'params':params}