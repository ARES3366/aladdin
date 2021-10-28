#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
import aiounittest
from auto_text_filter.text_spectral_cluster import spectral_cluster
from auto_text_filter.operate_atf_db import clusterResultGet,docsWordsPut,docsWordsDelete,condiGroupGet,groupGet,condiGroupPost,condiGroupPut,condiGroupDelete,conditionPost,conditionGet,conditionDelete,conditionPut,condidocsDelete
from auto_text_filter.text_filter import text_filter_,filter_analysis,text_multi_filter_,multi_analysis
import uuid
import asyncio
from auto_text_filter import atf_params_check 
import time

from client.milvus_client import AioMilvus
collection_name ='atf'
milvus_client = AioMilvus( collection_name,asyncio.get_event_loop())

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__),'test_doccluste_data', path))

#传入文件夹路径，读取文件，并把提取每个文件内容得关键词
def read_data_from_local(path):
    file_content={}
    content_paths = os.listdir(path)
    for content_name in content_paths:
        con_path=path+'/'+content_name
        print(con_path)
        content = ""
        with open(con_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for lin in lines:
                content += lin
        contentjs={}
        contentjs['content']=content
        file_content[content_name[:-4]]=contentjs
    return file_content

class TestTextCluster(aiounittest.AsyncTestCase):

    # group_id = None
    def get_event_loop(self):
        loop = asyncio.get_event_loop()
        return loop

    def check_result(self,result,equ):
        print(result)
        self.assertTrue(isinstance(result,dict))
        status = result['status']
        self.assertEqual(status,equ)
    #--------------------------word post--------
    #正常文本及cluster_num 正常 执行成功
    async def test_1text_cluster(self):
        # path="/root/myfile/data/cluster_test_data/4classall10_work"
        path='4classall10_work'
        path=_get_module_path(path)
        file_content = read_data_from_local(path)
        jobid = str(uuid.uuid1())       
        result =spectral_cluster(file_content,jobid,cluster_num=4)
        self.check_result(result,0)

        #正常task_id 返回正常信息
        json_data = await clusterResultGet(jobid)
        self.check_result(result,0)
        cluster_result = json_data["cluster_result"]
        self.assertTrue(isinstance(cluster_result, dict))

        #拿一个class_name和doc_name 做添加条件和修改等操作
        class_name=list(cluster_result.keys())[0]
        doc_name=cluster_result[class_name]['docs'][0]

        #把此文件修改状态为false
        json_data = await docsWordsPut(jobid,doc_name,0)
        self.check_result(json_data,0)

        #把此文件状态修改回来，为true
        json_data = await docsWordsPut(jobid,doc_name,1)
        self.check_result(json_data,0)
        
        
        #--------------------------- group post -------0-----
        group_name="机密条件"
        json_data = await condiGroupPost(group_name)
        self.check_result(json_data,0)
        group_id1 = json_data['group_id']
       
        #再增加一个条件分组，用于在查看条件分组时的信息
        group_name2="公司机密"
        json_data = await condiGroupPost(group_name2)
        self.check_result(json_data,0)
        group_id2 = json_data['group_id']
        
        #--------------------------- group put  --------0----
        # 正常传入group_id 和 groupname
        new_group_name="机密条件2"
        json_data3 = await condiGroupPut(group_id1,new_group_name)
        self.check_result(json_data3,0)
   
        #只查看所有的条件分组 
        groups_result = await groupGet()
        self.check_result(groups_result,0)
        groups=groups_result['groups']
        gs= list(groups.keys())

        #--------------------------- condition post   ------0---
        #新增条件
        cond_ids=[]
        i=1
        for cla_na in list(cluster_result.keys()):
            
            condi_name='condi_name'+str(i)
            result_data=await conditionPost(jobid,cla_na,group_id1,condi_name)
            print(result_data)
            i+=1
            self.check_result(result_data,0)
            condi_id=result_data['cond_id']
            cond_ids.append(condi_id)

        #--------------------------- condition get    ---------
        #查询条件,不传入cond_id     
        all_cond_data=await conditionGet()
        self.check_result(all_cond_data,0)
        conditions = all_cond_data['conditions']
        all_cond_num1 = len(conditions)

        #查询条件，传入cond_id
        conds=all_cond_data['conditions']
        cond_ids=list(conds.keys())
        for cid in cond_ids:
            c_data=await conditionGet(cond_id=cid)
            self.check_result(c_data,0)
        

        #------------------milvus 与MySQL 条件数量的检查
        #查看milvus中partition的数量是否与MySQL中的条件数一致
        # c_data = milvus_client.list_partition()
        # self.check_result(c_data,0)
        # list_partition = c_data['message']
        # self.assertEqual(len(list_partition)-1,all_cond_num1)

    
        #--------------------------- condition delete ------0---
        # cond_id 正常，doc_name正常
        result_data=await condidocsDelete(cond_ids[0],conds[cond_ids[0]]['docs'][0])
        time.sleep(2)
        self.check_result(result_data,0)
        
        #再次验证核对条件下的文本是否删除，条件下文本数量是否少一个
        #查询条件,不传入cond_id     
        all_cond_data2=await conditionGet()
        self.check_result(all_cond_data2,0)
        conditions2 = all_cond_data2['conditions']
        all_cond_num2 = len(conditions2)
        self.assertEqual(all_cond_num1,all_cond_num2)
        #查看数量是否一致
        self.assertEqual(len(conds[cond_ids[0]]['docs'])-1,len(conditions2[cond_ids[0]]['docs']))
        
        #查看milvus中的row_count 与MySQL的docs的数量是否一致
        collection_s = milvus_client.get_collection_stats()
        patitions = collection_s['message']['partitions']
        cond_ids_mil_num = 0
        for i in patitions:
            cond_ids_mil_num = i['row_count']
        doc_num=0
        for kk,vv in conditions2.items():
            doc_num+=len(vv['docs'])


        self.assertEqual(doc_num,cond_ids_mil_num)

        #删除条件
        result_data=await conditionDelete(cond_ids[0])
        self.check_result(result_data,0)
        time.sleep(3)
        #再次验证核对条件是否删除，条件数量是否少一个
        #查询条件,不传入cond_id     
        all_cond_data3=await conditionGet()
        self.check_result(all_cond_data3,0)
        conditions3 = all_cond_data3['conditions']
        all_cond_num3 = len(conditions3)

        self.assertEqual(all_cond_num1-1,all_cond_num3)
        time.sleep(2)

        #核对milvus中的partition是否也少一个
        # c_data2 = milvus_client.list_partition()
        # self.check_result(c_data2,0)
        # list_partition2 = c_data2['message']
        # self.assertEqual(len(list_partition2),all_cond_num3+1)
 
        
        #---------------------------- text_filter --------0-----
        # cond_id_list中cond_id 都不存在，错误返回
        # cond_id_list中cond_id 部分存在，正常返回
        # content包含中文简体、繁体，英文，正常返回
        # cond_id仅一个条件
        # cond_id_list 多个条件
        #conditions3

        # cond_list=['a0369132-bcee-11ea-a752-00505682b191','bb2079c2-bcee-11ea-b3fd-00505682b191']
        # path="/root/myfile/data/cluster_test_data/test"
        path='test'
        path=_get_module_path(path)
        content_paths = os.listdir(path)
        content=''
        for content_name in content_paths:
            con_path = path + '/' + content_name
            print(con_path)
            content = ""
            with open(con_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for lin in lines:
                    content += lin
            #单分类
            print('-------------单分类-----------')
            result = await text_filter_(content,list(conditions3.keys()))
            self.assertTrue(isinstance(result, dict))
            self.check_result(result,0)
            
            #多分类
            print('-------------多分类-----------')
            result = await text_multi_filter_(content,list(conditions3.keys()))
            self.assertTrue(isinstance(result, dict))
            self.check_result(result,0)
            



        
        
        #验证只有只传入一个条件时，返回这个条件的信息，及距离值
        print("---------单分类------============")
        result = await text_filter_(content,[list(conditions3.keys())[0]])
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)
        #验证传入多个条件时，有个正确，有的不正确，返回属于正确的的类别
        cond_ids_e=[list(conditions3.keys())[0]]
        cond_ids_e.append('111111111111111111111')
        result= await text_filter_(content,cond_ids_e)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)

        print('-------------------------------分析结果分析测试----------')
        #验证分类结果分析
        respect_id=list(conditions3.keys())[0]
        result= await filter_analysis(content,[],respect_id)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)

        #验证分类结果分析
        respect_id=list(conditions3.keys())[1]
        result= await filter_analysis(content,[],respect_id)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)
         
        
        #验证多分类结果分析
        print("-------------------------多分类结果分析----------------------")
        respect_id=list(conditions3.keys())[1]
        result= await multi_analysis(content,[],respect_id)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)

        #验证多分类结果分析
        print("-------------------------多分类结果分析----------------------")
        respect_id=list(conditions3.keys())[0]
        result= await multi_analysis(content,[],respect_id)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)

        # import pdb;pdb.set_trace()
        #验证传入多个类别，都是错误的类别是，返回的是错误信息
        condi_id_alle=[]
        condi_id_alle.append('123')
        condi_id_alle.append('321')
        result= await text_filter_(content,condi_id_alle)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)
        #验证传入空列表，返回正确信息
        condi_id_em=[]
        result= await text_filter_(content,condi_id_em)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,0)

        #传入的文本过短，只能提一个关键词，报错
        contenete='教授'
        condi_id_em=[]
        result= await text_filter_(contenete,condi_id_em)
        self.assertTrue(isinstance(result, dict))
        self.check_result(result,1)

        #删除条件分组
        # group_id='2748afa0-bc42-11ea-b228-00505682b191'
        for g in gs:
            json_data = await condiGroupDelete(g)
            print("--------------16----------------",json_data)
            status = json_data['status']
            self.assertEqual(status,0)
        time.sleep(2)
  
        #----------------------- word delete -------0----
       
        # 正常task_id 返回正常信息
        #清除此任务id下的数据
        result = await docsWordsDelete(jobid)
        print("--------------17----------------",result)
        status = result['status']
        self.assertEqual(status,0)



if __name__ == "__main__":
    unittest.main()
