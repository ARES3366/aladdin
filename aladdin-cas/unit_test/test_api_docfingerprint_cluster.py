#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from requests import session
import unittest
import numpy as np
import asyncio
from aiohttp import ClientSession
import time

fingerprints={1: '9313270044093412986', 2: '18247567279866345082', 3: '9313270301992777338', 4: '9313270301993170554', 5: '9313270044085548666', 6: '16230799071734494842', 7: '9295537120560641658', 8: '9297225970420905594', 9: '47566730110531194', 10: '9297241363583694458', 11: '18248411704796477050', 12: '9295818595537352314', 13: '9313270044093412986', 14: '17383720576341341818', 15: '9313270044093412986', 16: '9324262961347917434', 17: '18247567400125429370', 18: '13348495310687139450', 19: '17383720576341341818', 20: '9313270044093412986', 21: '13348495310687139450', 22: '14582490889423707346', 23: '1786529885637818291', 24: '281741990446863956', 25: '14511425885792740122', 26: '1320432095224941021', 27: '5287303492273845332', 28: '7087760399329022823', 29: '10064950060267610107', 30: '281741990446863956', 31: '7087760399329022823', 32: '281741990446863956', 33: '1320432095224941021', 34: '9771942017465441669', 35: '5406233584228355734', 36: '4197601370739363293', 37: '2209146094237983282', 38: '14582490889423707346', 39: '10736438249169907410', 40: '1786529885637818291', 41: '14739539184677547774', 42: '9234201416403084785', 43: '14277368999666539817', 44: '14582490889423707346', 45: '10064950060267610107', 46: '14582490889423707345', 47: '81741990446863956', 48: '6106389142591763941', 49: '4443764530545217475', 50: '5287303492273845332'}
fingerprints2={1: '', 2: '', 3: '', 4: '9313270301993170554', 5: '9313270044085548666', 6: '16230799071734494842', 7: '9295537120560641658', 8: '9297225970420905594', 9: '18247566730110531194', 10: '9297241363583694458', 11: '18248411704796477050', 12: '9295818595537352314', 13: '9313270044093412986', 14: '17383720576341341818', 15: '9313270044093412986', 16: '9324262961347917434', 17: '18247567400125429370', 18: '13348495310687139450', 19: '17383720576341341818', 20: '9313270044093412986', 21: '13348495310687139450', 22: '14582490889423707346', 23: '1786529885637818291', 24: '281741990446863956', 25: '14511425885792740122', 26: '1320432095224941021', 27: '5287303492273845332', 28: '7087760399329022823', 29: '10064950060267610107', 30: '281741990446863956', 31: '7087760399329022823', 32: '281741990446863956', 33: '1320432095224941021', 34: '9771942017465441669', 35: '5406233584228355734', 36: '4197601370739363293', 37: '2209146094237983282', 38: '14582490889423707346', 39: '10736438249169907410', 40: '1786529885637818291', 41: '14739539184677547774', 42: '9234201416403084785', 43: '14277368999666539817', 44: '14582490889423707346', 45: '10064950060267610107', 46: '14582490889423707345', 47: '281741990446863956', 48: '6106389142591763941', 49: '4443764530545217475', 50: ''}

fingerprints3={1: '0', 2: '18247567279866345082', 3: '0', 4: '9313270301993170554', 5: '9313270044085548666', 6: '16230799071734494842', 7: '9295537120560641658', 8: '9297225970420905594', 9: '18247566730110531194', 10: '9297241363583694458', 11: '18248411704796477050', 12: '9295818595537352314', 13: '9313270044093412986', 14: '17383720576341341818', 15: '9313270044093412986', 16: '9324262961347917434', 17: '18247567400125429370', 18: '13348495310687139450', 19: '17383720576341341818', 20: '9313270044093412986', 21: '13348495310687139450', 22: '14582490889423707346', 23: '1786529885637818291', 24: '281741990446863956', 25: '14511425885792740122', 26: '1320432095224941021', 27: '5287303492273845332', 28: '7087760399329022823', 29: '10064950060267610107', 30: '281741990446863956'}
fingerprints4={'测试1': '955090963809210198', '测试11': '955090963809210198', '测试111': '955090963809210198', '测试2': '1098916499030077252', '测试1111': '955090963809210193', '测试2111': '955090963809226577', '测试20': '2152232420907678608', '测试21': '7945592162292235283', '测试22': '1098925295139868500', '测试222': '1098916499030077252', '测试2222': '1098916499046854612', '测试23': '6204084072471907983', '测试3': '9805261667929757901', '测试30': '560115195044805430', '测试31': '595716273722019476', '测试32': '3045693299587154821', '测试33': '9805261908447922381', '测试333': '10088987310582728909', '测试3333': '9805261667929757901', '测试6': '5638552833239999629', '测试66': '5350322465678222477', '测试666': '5350322457088287885', '测试6666': '5638552833240917133', '测试7': '1100049271422122500', '测试8': '5494560524312569485', '测试88': '5494560515722634893', '测试888': '5495123474265990285', '测试8888': '5638675712388425357', '测试9': '1098925295123100262', '测试空1': '', '测试空2': '', '测试空3': ''}

url_doccluster = "http://127.0.0.1:9528/api/fast-text-analysis/v1/doc-fingerprint-cluster"
class TestApi(unittest.TestCase):
   
    def test_doccluster(self):
       
        global fingerprints
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad" : grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,0)
        message = json_data["similardocs_set"]
        self.assertTrue(isinstance(message, list))
        sess.close()
    
    def test_doccluster11(self):

        fingerprints={}
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad" : grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,0)
        message = json_data["similardocs_set"]
        self.assertTrue(isinstance(message, list))
        sess.close()

    def test_doccluster12(self):

        global fingerprints3
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints3,
            "grad" : grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,0)
        message = json_data["similardocs_set"]
        self.assertTrue(isinstance(message, list))
        sess.close()

    def test_doccluster13(self):

        global fingerprints4
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints4,
            "grad" : grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        sess.close()


    def test_doccluster2(self):
        '''
        参数不正常，grad的取值范围小于预定值
        '''
        global fingerprints
        grad = 1
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad":grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        message = json_data["message"]
        self.assertTrue(isinstance(message, str))
        sess.close()
    def test_doccluster3(self):
        '''
        参数不正常，grad的取值范围大于预定值
        '''
        global fingerprints
        grad = 7
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad":grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        message = json_data["message"]
        self.assertTrue(isinstance(message, str))
        sess.close()
    def test_doccluster4(self):
        '''
        参数不正常，grad不是int格式
        '''
        global fingerprints
        grad = "7"
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad":grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        message = json_data["message"]
        self.assertTrue(isinstance(message, str))
        sess.close()
    def test_doccluster5(self):
        '''
        参数不正常，grad不是int格式
        '''
        global fingerprints
        grad = [4]
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad":grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        message = json_data["message"]
        self.assertTrue(isinstance(message, str))
        sess.close()
    def test_doccluster6(self):
        '''
        参数不正常，没有fingerprints参数
        '''
        grad = 4
        sess = session()
        url = url_doccluster
        params = {
           
            "grad":grad
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        message = json_data["message"]
        self.assertTrue(isinstance(message, str))
        sess.close()
    def test_doccluster7(self):
        '''
         参数不正常，没有grad参数
        '''
        global fingerprints
        
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints
        }
        s_get = sess.post(url, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,1)
        message = json_data["message"]
        self.assertTrue(isinstance(message, str))
        sess.close()
    

    def test_doccluster8(self):
        '''
        参数正常，
        测试效率
        '''
        global fingerprints
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints,
            "grad" : grad
        }
        import time
        sumtime=0
        for i in range(100):
            start = time.time()
            s_get = sess.post(url, json=params)
            end = time.time()
            sumtime += end-start
            json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        sess.close()
        print('50个指纹列表cluster平均每s处理请求数量：',1000/sumtime)


    def test_doccluster9(self):
        '''
        参数正常，
        测试效率
        '''
        global fingerprints2
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints2,
            "grad" : grad
        }
        import time
        sumtime=0
        for i in range(100):
            start = time.time()
            s_get = sess.post(url, json=params)
            end = time.time()
            sumtime += end-start
            json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        sess.close()
        print('30个指纹列表cluster平均每s处理请求数量：',1000/sumtime)
    def test_doccluster99(self):
        '''
        参数正常，
        测试效率
        '''
        fingerprints6={"t1":"5568563","t2":"","t3":"5568563","t4":157554267,"t5":"","t6":""}
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints6,
            "grad" : grad
        }
        import time
        sumtime=0
        for i in range(100):
            start = time.time()
            s_get = sess.post(url, json=params)
            end = time.time()
            sumtime += end-start
            json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        sess.close()
        print('30个指纹列表cluster平均每s处理请求数量：',1000/sumtime)
    def test_doccluster991(self):
        '''
        参数正常，
        测试效率
        '''
        fingerprints6={"t1":"5568563"}
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints6,
            "grad" : grad
        }
        import time
        s_get = sess.post(url, json=params)
       
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,0)
        sess.close()
    def test_doccluster992(self):
        '''
        参数正常，
        测试效率
        '''
        fingerprints6={"t1":"5568563","t3":"5568563"}
        grad = 3
        sess = session()
        url = url_doccluster
        params = {
            "fingerprints": fingerprints6,
            "grad" : grad
        }
        import time
        s_get = sess.post(url, json=params)
       
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,0)
        sess.close()
