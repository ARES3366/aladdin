#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from requests import session
import unittest
import numpy as np
import asyncio
from aiohttp import ClientSession
import time
import os

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__),'test_doccluste_data', path))

#传入文件夹路径，读取文件，并把提取每个文件内容得关键词
def read_data_from_local(path):
    file_content={}
    content_paths = os.listdir(path)
    for content_name in content_paths:
        con_path=path+'/'+content_name
        # print(con_path)
        content = ""
        with open(con_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for lin in lines:
                content += lin
        contentjs={}
        contentjs['content']=content
        file_content[content_name[:-4]]=contentjs
    return file_content




class TestApi(unittest.TestCase):
    def test_1doc_cluster(self):
        #聚类API,查询聚类结果，根据结果修改或撤销修改一个文本是否参与条件关键词的提取
        url_word = "http://127.0.0.1:9528/api/auto-text-filter/v1/word"
        #参数正常，返回聚类任务id
        # path="/root/myfile/data/cluster_test_data/4classall10_work"
        path='4classall10_work'
        path=_get_module_path(path)
        print("==========================path==================",path)
        file_content = read_data_from_local(path)
          
        sess = session()
        params = {
            "contents":file_content,
            "cluster_num":4
        }
        s_get = sess.post(url_word, json=params)
        # if s_get.status_code
        json_data = json.loads(s_get.content.decode('utf8'))
        print("--------------doc_cluster 1------------------",json_data)
        self.assertEqual(s_get.status_code,200)
        taskid = json_data["taskid"]
        self.assertTrue(isinstance(taskid, str))
        
        # 正常参数（taskid）,根据聚类任务查询聚类结果
        par = {
            "taskid":taskid
        }
        s_get = sess.get(url_word, params=par)
        json_data = json.loads(s_get.content.decode('utf8'))
        print("--------------doc_cluster 2------------------",json_data)
        self.assertEqual(s_get.status_code,200)
        cluster_result = json_data["cluster_result"]
        self.cluster_result=cluster_result
        self.assertTrue(isinstance(cluster_result, dict))
        
        par2 = {
        }
        s_get2 = sess.get(url_word, params=par2)
        print('----s_get2.content ',s_get2.content)
        json_data_err = json.loads(s_get2.content.decode('utf8'))
        print("--------------doc_cluster 2-1-----------------",json_data_err)
        self.assertEqual(s_get2.status_code,400)
        
        
        #找一个聚类结果下的类别及此类别下的文件
        class_names=list(cluster_result.keys())
        class_name=class_names[0]
        doc_name=cluster_result[class_name]['docs'][0]
        action=0


        # 不正常参数（taskid）
        taskid_error='e576d894-bb70-11ea-a59c-00505682b'
        params = {
            "taskid":taskid_error
        }
        s_get = sess.get(url_word, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print("--------------doc_cluster 3------------------",json_data)
        self.assertEqual(s_get.status_code,400)
    
        #参数正常，操作文件不参与条件关键词的提取 
        params = {
            "taskid":taskid,
            "doc_name":doc_name,
            "action":action
        }
        s_get = sess.put(url_word, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)

        #参数正常，重复操作，会报错   
        s_get = sess.put(url_word, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,500)

        #参数正常，撤回操作文件不参与条件关键词的提取
        action = 1
        params = {
            "taskid":taskid,
            "class_name" : class_name,
            "doc_name":doc_name,
            "action":action
        }
        s_get = sess.put(url_word, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,200)


        #===============条件分组API测试
        url_group = "http://127.0.0.1:9528/api/auto-text-filter/v1/group"
        #新增条件分组
        #参数正常，返回条件condi_grou[分组
        params = {
            "group_name":"敏感条件"
        }
       
        s_get = sess.post(url_group, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,200)
        group_id = json_data["group_id"]
        self.assertTrue(isinstance(group_id, str))
        print("--------------group 1------------------",json_data)
        params = {
            "group_name":"敏感条件333"
        }
       
        s_get = sess.post(url_group, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,200)
        group_id333 = json_data["group_id"]
        self.assertTrue(isinstance(group_id333, str))
        print("--------------group 2------------------",json_data)
        ## 正常参数（content），重复插入会报错
        params = {
            "group_name":"敏感条件"
        }
        s_get = sess.post(url_group, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,500)

       #修改分组名称
        new_group_name = "敏感文件2"
        params = {
            "group_id":group_id,
            "group_name":new_group_name
        }
        s_get = sess.put(url_group, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,200)

        new_group_name = "敏感文件"
        params = {
            "group_id":group_id,
            "group_name":new_group_name
        }
        s_get = sess.put(url_group, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,200)
        print("--------------group 3------------------",json_data)

        #条件API测试
        #新增条件
        url_condition = "http://127.0.0.1:9528/api/auto-text-filter/v1/condition"
        condi_ids=[]       
        i=1
        for cname in class_names:        
            condi_name='condi_name'+str(i)
            #参数正常，
            params = {
                "taskid":taskid,
                "class_name":cname,
                "group_id":group_id,
                "cond_name":condi_name
            }
            s_get = sess.post(url_condition, json=params)
            json_data = json.loads(s_get.content.decode('utf8'))
            print(json_data)
            self.assertEqual(s_get.status_code,200)
            condi_id = json_data['cond_id']
            condi_ids.append(condi_id)
            i+=1
        # condi_id = condi_ids[0]
        ## 正常参数（content），重复插入会报错
        params = {
            "taskid":taskid,
            "class_name":class_name,
            "group_id":group_id,
            "cond_name":'condi_name1'
        }
        s_get = sess.post(url_condition, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        self.assertEqual(s_get.status_code,500)

        #查询条件分组
        parg = {
            "group_id":''
        }
        s_getg = sess.get(url_group, params=parg)
        json_datag = json.loads(s_getg.content.decode('utf8'))
        self.assertEqual(s_getg.status_code,400)

        #查询条件分组,传入groupid
        para = {
            "only":str(1),
            "group_id":group_id
        }
        s_get = sess.get(url_group, params=para)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        groups = json_data["groups"]
        self.assertTrue(isinstance(groups, dict))

        #查询条件分组,传入groupid
        paramss = {
            "only":str(0),
            "group_id":group_id333
        }
        s_get = sess.get(url_group, params=paramss)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        groups = json_data["groups"]
        self.assertTrue(isinstance(groups, dict))


        #查询条件分组
        params = {
            'only':'1'
        }
        s_get = sess.get(url_group, params=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        all_groups = json_data["groups"]
        self.assertTrue(isinstance(all_groups, dict))



        #查询条件
        para = {
            
        }
        s_get = sess.get(url_condition, params=para)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        conditions = json_data["conditions"]
        self.assertTrue(isinstance(conditions, dict))

        #查询条件,传入cond_id
        param = {
            "cond_id":condi_ids[0]
        }
        s_get = sess.get(url_condition, params=param)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        conditions = json_data["conditions"]
        self.assertTrue(isinstance(conditions, dict))


       #修改条件名
        new_condi_name = "修改后的名字"
        params = {
            "cond_id":condi_ids[0],
            "cond_name":new_condi_name
        }
        s_get = sess.put(url_condition, json=params)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)

        #传入条件id和docname  删除条件下一个文件，不可撤销
        condi_idde=condi_ids[0]
        doc_named=conditions[condi_idde]['docs'][0]
        params_cd = {
            "cond_id":condi_idde,
            "doc_name":doc_named
        }
        s_get = sess.delete(url_condition, params=params_cd)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        time.sleep(2)
        #重复删除会报错
        s_get = sess.delete(url_condition, params=params_cd)
        json_data = json.loads(s_get.content.decode('utf8'))
        print("----------------------32-----")
        print(json_data)
        self.assertEqual(s_get.status_code,500)
        
        #传入条件，不传入docname，删除整个条件
        params_c = {
            "cond_id":condi_idde
        }
        s_get = sess.delete(url_condition, params=params_c)
        json_data = json.loads(s_get.content.decode('utf8')) 
        print(json_data)
        self.assertEqual(s_get.status_code,200)
        time.sleep(3)

        ## 错误参数（content）
        params_c = {
            "cond_id":'1111111111111111111111111111'
        }
        s_get = sess.delete(url_condition, params=params_c)
        print(s_get.content)
        json_data = json.loads(s_get.content.decode('utf8'))
        print(json_data)
        self.assertEqual(s_get.status_code,500)
        #对文件进行识别，是敏感文件会返回类别
        url_senti_tag = "http://127.0.0.1:9528/api/auto-text-filter/v1/text_filter"
        #参数正常，
        # path="/root/myfile/data/cluster_test_data/test"
        path='test'
        path=_get_module_path(path)
        print("----------------------33-----")
        # cond_id_list=[]
        # for con_id in cond_ids:
        #     cond_id_list.append(con_id)
        condi_ids.remove(condi_idde)
        content_paths = os.listdir(path)
        for content_name in content_paths:
            con_path = path + '/' + content_name
            print(con_path)
            content = ""
            with open(con_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for lin in lines:
                    content += lin

            params = {
                "condition":[],
                "content":content
            }
            s_get = sess.post(url_senti_tag, json=params)
            json_data = json.loads(s_get.content.decode('utf8'))
            print(json_data)
            self.assertEqual(s_get.status_code,200)
        
        #删除条件
        for condi_id in condi_ids:
            paramsd={
                "cond_id":condi_id
            }
            res_delete=sess.delete(url_condition,params=paramsd)
            res_data = json.loads(res_delete.content.decode('utf8'))
            print(res_data)
            self.assertEqual(res_delete.status_code,200)
            time.sleep(2)

        #删除条件分组
        for gid in all_groups.keys():
            paramsd={
                "group_id":gid
            }
            res_delete=sess.delete(url_group,params=paramsd)
            res_data = json.loads(res_delete.content.decode('utf8'))
            print(res_data)
            self.assertEqual(res_delete.status_code,200)
            time.sleep(2)

        #清除聚类任务下数据
        paramst={
            "taskid":taskid
        }
        res_delete=sess.delete(url_word,params=paramst)
        res_data = json.loads(res_delete.content.decode('utf8'))
        print(res_data)
        self.assertEqual(res_delete.status_code,200)
        sess.close()
        

        
    


