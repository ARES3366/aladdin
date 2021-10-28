#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from requests import session
import unittest
import numpy as np


url = "http://127.0.0.1:9528/api/fast-text-analysis/v1/privacy-properties"
class TestApiPorpertySensitive(unittest.TestCase):
    def test_update_property(self):
        '''
        参数:
		修改类别为update，id和bank为true，其他为false
	期望结果：
		返回的识别信息列表有两个信息cn_id和cn_bank
        '''
        global  url
        sess = session()
        params = {
            "parameter":
                 {"recognize_class":"update",
                  "rate_grade":"高",
                  "update_propertiy":{
                                     "cn_id":"true",
                                     "cn_bank":"true",
                                     "cn_email":"true",
                                     "cn_date":"false",
                                     "cn_telephone":"true",
                                     "cn_passport":"false"
                                    }
                 }
        }
        s_get = sess.put(url, json=params)
        
        json_data = json.loads(s_get.content.decode('utf8'))
        print("修改：")
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 0)
        class_message = json_data['class_message']
        self.assertEqual(4, len(class_message))
        print(type(class_message))
        sess.close()
    def test_default_property(self):
        '''
        参数:
                修改类别为defalut，
        期望结果：
                返回的识别信息列表有四个信息cn_id、cn_bank、cn_email、cn_telephon
        '''
        global url
        sess = session()
        params = {
            "parameter":
                 {"recognize_class":"default",
                  "rate_grade":"高",
                  "update_propertiy":{
                                     "cn_id":"true",
                                     "cn_bank":"true",
                                     "cn_email":"false",
                                     "cn_date":"false",
                                     "cn_telephon":"false",
                                     "cn_passport":"false"
                                    }
                 }
        }
        s_get = sess.put(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print("默认")
        print(json_data)
        status = json_data['status']
        self.assertEqual(status, 0)
        class_message = json_data['class_message']
        
        self.assertEqual(4, len(class_message))
        print(type(class_message))
        sess.close()



#tp = TestApiPorpertySensitive()
#tp.test_update_property()
#tp.test_default_property()
#tp.test_check_property()




