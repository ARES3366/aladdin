#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import json
import tornado.web
from analysis_package.common_classify import common_classify

class CommonClassifyHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1,
        }
        try:
            params = json.loads(self.request.body.decode())
            content = params['content']
            #content_len = len(content)
            return_result = await common_classify.apredict(content = content[:10000])
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            self.write(return_result)

class BatchCommonClassifyHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        return_result = {
            "status": 1,
        }
        try:
            params = json.loads(self.request.body.decode())
            content_list = params['content_list']
            if len(content_list)==0:
                return_result['message'] = 'content list length can`t be 0'
                self.set_status(400)
                return self.write(return_result)
            if len(content_list)>100:
                return_result['message'] = 'content list length is bigger than 100'
                self.set_status(400)
                return self.write(return_result)
            for i in range(len(content_list)):
                content_list[i] = content_list[i][:10000]
            return_result = common_classify.batch_text_classify(content_list = content_list)
            return_result['status'] = 0
            return self.write(return_result)
        except Exception as e:
            traceback.print_exc()
            print(e)
            return_result["message"]=str(e)
            self.set_status(400)
            self.write(return_result)

