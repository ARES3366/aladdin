#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
import aiounittest
from auto_text_filter.text_spectral_cluster import spectral_cluster,extract_
from auto_text_filter.operate_atf_db import clusterResultGet,docsWordsPut,docsWordsDelete,condiGroupGet,groupGet,condiGroupPost,condiGroupPut,condiGroupDelete,conditionPost,conditionGet,conditionDelete,conditionPut,condidocsDelete,conditionAssignPost
from auto_text_filter.text_filter import text_filter_
import uuid
import asyncio
from auto_text_filter import atf_params_check 
import time


# from auto_text_filter.milvus_client import AioMilvus
# # collection_name = milvus_config["collection"]
# collection_name ='atf'
# milvus_client = AioMilvus(asyncio.get_event_loop(), collection_name)


# collection_name = milvus_config["collection"]



class TestTextCluster(aiounittest.AsyncTestCase):

    # group_id = None
    def get_event_loop(self):
        loop = asyncio.get_event_loop()
        return loop
  
    #用于验证结果，返回的status值是否与预期一致
    def result(self,json_data,equal):
        print(json_data)
        status = json_data['status']
        self.assertEqual(status,equal)
    #用于添加聚类任务，用于聚类数据的修改，测试条件的添加等
    def text_cluster(self,jobid):
        #text数量多余10个，正常
        file_content={
            '1':{'content':'恢复的时候，会用srvctlstopdatabase-dxxx来停止ORACLE实例，如果这个命令执行有错，则恢复失败，请先确保数据库实例可以用srvctlstopdatabase-dxxx命令正常停止。恢复到单机的情况下，请确保归档路径与备份的RAC节点的归档路径一致'},
            '2':{'content':'创建虚拟客户端点击【客户端名称】列表有上方的小齿轮下拉列表，点击【新建虚拟客户端】，从弹出的虚拟客户端类型中选择“ORACLERAC客户端'},
            '3':{'content':'以便管理；配置客户端：该选项用来重删任务数据设置，根据用户的实际资源情况，设置对应的数值即可，其中内存使用限制越大，性能越好；新建虚拟客户端：在此选项中，用户可以选择创建双机、集群'},
            '4':{'content':'添加对应的授权后，即可解决；添加授权在控制台界面，【运营管理】【授权管理】中添加，输入对应的授权码，点击在线激活，即可；第六章定时恢复最佳实践6.1GBase恢复概述\tAnyBackup5.01.0版本针对用户的实际需求提供时间点恢复方式'},
            '5':{'content':'默认为恢复至原客户端原位置注意：此处可以选择恢复至其他位置，如果是异机恢复，则异机上GBase数据库的安装路径和数据文件路径必须和原机相同点击下一步，填写执行备注信息，点击完成，任务即执行'},
            '6':{'content':'这允许你同时运行多个操作系统在一台物理计算机。Hyper-V提供了软件基础设施和基本的管理工具，可用于创建和管理虚拟服务器计算环境。2、Hyper-V备份恢复功能模块简介Hyper-V调用VolumeShadowCopyService'},
            '7':{'content':'点击完成后开始恢复：注释：如果恢复到原客户端，且原客户端上被备份的虚拟机没有删除，必须勾选强制覆盖，否则无法进行虚拟机恢复。5、开始恢复恢复时的信息如下：如上图所示，开始恢复虚拟机'},
            '8':{'content':'重新授权实例选择数据源，保存后再次备份）·Q：mysqlforlinux的环境，创建mysql定时备份任务，未添加实例授权，直接展开实例节点，提示连接实例失败（而非提示实例未授权）？A：此现象属于正常情况'},
            '9':{'content':'当环境出现备份或恢复速度较慢，怎样解决?首先查看存储柜的cached值，如果cached值小于6GB时，可以使用以下方法进行性能调优。1.打开/etc/sysctl.conf文件。#vi/etc/sysctl.conf2.修改如下参数的值为下方参数对应的值'},
            '10':{'content':'通过下面展开ORACLE实例是发现不了问题的，这样会导致接下来备份失败。授权完以后一定要检查一下授权是否有误，展开ORACLE实例，看是否能正常显示所有的表空间'}
        }     
        result =spectral_cluster(file_content,jobid,cluster_num=3)
        self.result(result,0)
    
    #-------------------------------------word post-----------
    async def test_text_cluster(self):
        #text数量不少于10个，但是其中八个文本中的文字很少，能聚类的文本只有2个，聚类个数为3,报错
        file_content={
            '1':{'content':'恢复的时候，会用srvctlstopdatabase-dxxx来停止ORACLE实例，如果这个命令执行有错，则恢复失败，请先确保数据库实例可以用srvctlstopdatabase-dxxx命令正常停止。恢复到单机的情况下，请确保归档路径与备份的RAC节点的归档路径一致'},
            '2':{'content':'创建虚拟客户端点击【客户端名称】列表有上方的小齿轮下拉列表，点击【新建虚拟客户端】，从弹出的虚拟客户端类型中选择“ORACLERAC客户端'},
            '3':{'content':'................'},
            '4':{'content':'111111111111111'},
            '5':{'content':'22222222222'},
            '6':{'content':'333333333333333333'},
            '7':{'content':'444444444444444444'},
            '8':{'content':'5555555555555555'},
            '9':{'content':'6666666666666'},
            '10':{'content':'55555555555555'}
        }
        jobid = str(uuid.uuid1())       
        result =spectral_cluster(file_content,jobid,cluster_num=3)
        print("---------------1----------------",result)
        self.assertTrue(isinstance(result,dict))
        self.result(result,1) 
        
        #text数量多余10个，正常
        file_content_eng={
            '1':{'content':'According to thorough epidemiological investigations on the two cases, Tianjin found the source of the two infections could be traced to two batches of pig heads imported from North America'},
            '2':{'content':'which were carried in and out by the same worker while wearing the same pair of gloves and clothes. The original source is likely the pig heads which then infected the pig knuckles, according to Zhang'},
            '3':{'content':'four residents in the Kanhaixuan residential community in the city s Dongjianggang district reported to be confirmed cases of COVID-19. On November 9'},
            '4':{'content':'The differences lie in the virus strain via virus sequencing and transmission patterns - one virus strain is the L genotype of the European branch I and the other is from North America'},
            '5':{'content':'The source of the Hailian cold storage is frozen pig heads imported from North America. Zhang explained how two working staff who had contacts with the pig heads were infected'},
            '6':{'content':'Based on closed-circuit videos in buildings of the Kanhai residential community, confirmed cases entered elevators coughing and wearing no masks, which may have spread the virus, according to Zhang'},
            '7':{'content':'ianjin lowered the risk level of a street in Binhai New Area and two districts of a logistics center in Zhongxinyugang.'},
            '8':{'content':' North China  Tianjin Municipality have two sources, with one related to frozen pig heads imported from North America, Zhang Ying, a deputy director of Tianjin diseases control and prevention center, told a press conference on Tuesday.'},
            '9':{'content':'When Japan evacuated its nationals from Wuhan in January, it had to seek assistance from the Japanese Embassy in Beijing, which led to the suggestion of setting up a consulate in the city.'},
            '10':{'content':'Despite challenges, the main theme of the bilateral relationship is cooperation, and the two countries have much common ground for cooperation, including frequent people-to-people exchanges, '}
        }     
        jobid_eg = str(uuid.uuid1())       
        result =spectral_cluster(file_content_eng,jobid_eg)
        print("---------------1----------------",result)
        self.assertTrue(isinstance(result,dict))
        self.result(result,0)
        #删除数据
        await self.word_delete(jobid_eg,0) 
        time.sleep(2)

    #-------------------------- word get -----------
    async def test_word_get(self):
        #测试准备，正常文本聚类
        jobid = str(uuid.uuid1())
        self.text_cluster(jobid)
        # task_id.append(jobid)
        #报错，错误task-id 返回错误信息
        json_data = await clusterResultGet('123456')
        self.result(json_data,1)
        #正常，传入正确jobid，返回正常信息
        json_data = await clusterResultGet(jobid)
        self.result(json_data,0)

        #删除数据
        await self.word_delete(jobid,0)
        time.sleep(2)

    #-------------------------------------word put-----------  
    async def word_put(self,taskid,docname,action,equal):    
        json_data = await docsWordsPut(taskid,docname,action)
        self.result(json_data,equal)
    async def test_word_put(self):
        #测试准备，正常文本聚类
        jobid = str(uuid.uuid1())
        self.text_cluster(jobid)
        # task_id.append(jobid)
        #测试准备，正常task_id 返回正常信息
        json_data = await clusterResultGet(jobid)
        self.result(json_data,0)
        cluster_result = json_data["cluster_result"]
        #测试准备，取出一个class和doc用于进行修改
        class_name=list(cluster_result.keys())[0]
        doc_name=cluster_result[class_name]['docs'][0]
        
        #报错，错误task-id 返回错误信息
        taskid='1111111'
        await self.word_put(taskid,doc_name,0,1)
        #报错，正常task_id 文件名错误，返回错误信息
        await self.word_put(jobid,'doc_name',0,1)
        #报错，正常id ，正确文件名，操作类别不符合要求，返回错误信息
        await self.word_put(jobid,doc_name,2,1)

        #正确，正常参数修改
        await self.word_put(jobid,doc_name,0,0)

        #验证，正常修改后，修改是否有效果
        json_data = await clusterResultGet(jobid)
        self.result(json_data,0)
        cluster_result = json_data["cluster_result"]
        self.assertNotIn(doc_name,cluster_result[class_name]['docs'])

        #删除数据
        await self.word_delete(jobid,0)
        time.sleep(2)


    #--------------------------- group post -------0-----
    async def group_post(self,group_name,equal):
        json_data = await condiGroupPost(group_name)
        self.result(json_data,equal)
        group_id1 = json_data['group_id']
        return group_id1
    async def test_group_post(self):  
        # 正常添加
        group_name="机密条件"
        gid = await self.group_post(group_name,0) 

        #验证，是否有此条件分组
        groups = await self.groups_get()
        self.assertIn(group_name,list(groups.values()))
        #报错，重复添加会报错
        json_data = await condiGroupPost(group_name)
        self.result(json_data,1)

        #删除分组数据
        await self.group_delete(gid,0)
        time.sleep(2)
       
    #--------------------------- group put -------0-----
    async def group_put(self,group_id,group_name,equal):
        json_data3 = await condiGroupPut(group_id,group_name)
        self.result(json_data3,equal)
    #查看group_name,#只查看条件分组信息，用于验证分组修改后名称是否改变
    
    async def test_group_put(self):
        #先添加一个分组，
        group_name="上海"
        group_id1 = await self.group_post(group_name,0)
        print("=====================group_id",group_id1)  
        #验证，在修改前进行查看是否有这个分组
        groups1 = await self.groups_get()
        self.assertIn(group_name,list(groups1.values()))
        # 正常传入group_id 和 groupname
        #修改条件分组名称
        new_group_name="上海2"
        await self.group_put(group_id1,new_group_name,0)
        #验证，在修改后进行查看是否有修改后的分组名称
        groups2 = await self.groups_get()
        self.assertIn(new_group_name,list(groups2.values()))

        # 错误的group——id 报错
        #修改条件分组名称
        new_group_name_er="上海error"
        gid = '1231231213'
        await self.group_put(gid,new_group_name_er,1)
        #修改条件分组名称,重复修改报错
        await self.group_put(group_id1,new_group_name,1)

        #删除条件分组数据
        await self.group_delete(group_id1,0)
        time.sleep(2)
    


    #--------------------------- group get -------0-----
    async def groups_get(self):    
        only_group_all = await groupGet()
        self.result(only_group_all,0)
        grs=only_group_all['groups']
        return grs
       
    
    async def test_group_get(self):  
        #准备，测试数据
        jobid = str(uuid.uuid1()) 
        cluster_result,group_id =await self.condition_data(jobid,'中国上海爱数')
        #再添加一个group_name,用于验证查询出的结果
        json_data = await condiGroupPost('中国上海爱数2')
        group_id2 = json_data['group_id']
        #正常添加，
        
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='condi_name1'+str(i)
            await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1
        #测试
        #报错，只查看条件分组信息，传入错误条件分组id
        only_group_error = await groupGet('11111')
        self.result(only_group_error,1)
        
        #验证，只查看条件分组信息，不传入条件分组id，返回两个分组数据
        only_group_all = await groupGet()
        self.result(only_group_all,0)
        grs=only_group_all['groups']
        gps_id= list(grs.keys())
        print(gps_id)
        #验证，传入正确的条件分组id，只查看条件分组信息，只有一个条件分组的信息，
        only_group = await groupGet(gps_id[0])
        self.result(only_group,0)
        #验证，传入正确的条件分组id，只查看条件分组信息，只有一个条件分组的信息，
        only_group = await groupGet(gps_id[1])
        self.result(only_group,0)
        grs2=only_group['groups']
        gps_id2= list(grs2.keys())
        self.assertEqual(len(gps_id2),1)
        
        #测试，包含条件的条件分组
        #传入错误group_id 
        groups_error = await condiGroupGet(group_id="gp_id")
        self.result(groups_error,1)
        #查看条件分组信息，不传入条件分组id，返回所有的分组及条件信息
        groups_condi_result2 = await condiGroupGet()
        self.result(groups_condi_result2,0)
        grs=groups_condi_result2['groups']
        gps= list(grs.keys())
        self.assertEqual(len(gps),2)
        
        #查看条件分组信息，传入条件分组id
        groups_condi = await condiGroupGet(group_id=group_id)
        self.result(groups_condi,0)

        #查看条件分组信息，传入条件分组id
        groups_condi2 = await condiGroupGet(group_id=group_id2)
        self.result(groups_condi2,0)
        grs=groups_condi2['groups']
        cids = grs[group_id2]['condis'].keys()
        #验证，没有在group_id2中添加条件数据，所以查询到的condis为{None:None},只有一个元素并且是None
        self.assertEqual(len(cids),1)
        self.assertIn(None,cids)

        #删除数据
        await self.word_delete(jobid,0)
        await self.group_delete(group_id,0)
        await self.group_delete(group_id2,0)
        time.sleep(2)
            
        
     
    
    #准备数据，为condition post ，put，delete提供数据
    async def condition_data(self,jobid,group_name): 
        #准备，测试数据
        self.text_cluster(jobid)
        # task_id.append(jobid)
        #准备，先添加一个分组，
        json_data = await condiGroupPost(group_name)
        print(json_data)
        group_id = json_data['group_id']
        self.result(json_data,0)
        #准备，正常task_id 返回正常信息
        json_data = await clusterResultGet(jobid)

        self.result(json_data,0)
        cluster_result = json_data["cluster_result"]
        self.assertTrue(isinstance(cluster_result, dict))
    
        return cluster_result,group_id

    #------------------------------------------condition post-------------
    #测试相同的文本插入时会返回有相似文本的数据
    async def test_condition_post2(self):
        #准备，测试数据 
        jobid = str(uuid.uuid1()) 
        cluster_result,group_id =await self.condition_data(jobid,'上海爱数ai')
        #正常添加，
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='condi_name2'+str(i)
            await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1
        await self.check_condition_post(jobid,list(cluster_result.keys())[0],group_id,'condi_name221',0)

        #删除数据
        await self.word_delete(jobid,0)
        await self.group_delete(group_id,0)
        time.sleep(2)
        
    #为测试添加条件，有个别相同的文本时
    #用于添加聚类任务，用于聚类数据的修改，测试条件的添加等
    def text_cluster2(self,jobid):
        #text数量多余10个，正常
        file_content={
            '1':{'content':'恢复的时候，会用srvctlstopdatabase-dxxx来停止ORACLE实例，如果这个命令执行有错，则恢复失败，请先确保数据库实例可以用srvctlstopdatabase-dxxx命令正常停止。恢复到单机的情况下，请确保归档路径与备份的RAC节点的归档路径一致'},
            '22':{'content':'创建虚拟客户端点击【客户端名称】列表有上方的小齿轮下拉列表，点击【新建虚拟客户端】，从弹出的虚拟客户端类型中选择“ORACLERAC客户端'},
            '3':{'content':'以便管理；配置客户端：该选项用来重删任务数据设置，根据用户的实际资源情况，设置对应的数值即可，其中内存使用限制越大，性能越好；新建虚拟客户端：在此选项中，用户可以选择创建双机、集群'},
            '44':{'content':'添加对应的授权后，即可解决；添加授权在控制台界面，【运营管理】【授权管理】中添加，输入对应的授权码，点击在线激活，即可；第六章定时恢复最佳实践6.1GBase恢复概述\tAnyBackup5.01.0版本针对用户的实际需求提供时间点恢复方式'},
            '55':{'content':'默认为恢复至原客户端原位置注意：此处可以选择恢复至其他位置，如果是异机恢复，则异机上GBase数据库的安装路径和数据文件路径必须和原机相同点击下一步，填写执行备注信息，点击完成，任务即执行'},
            '66':{'content':'机械租赁行业企业的情况。我们发现2017年来企业成立数量持续高增长，我们认为主要反映了塔吊从建筑企业自有向租赁市场转变的情况。我们发现近年来企业成立数量持续增加，今年年初受疫情影响成立数量大幅下降'},
            '77':{'content':'内装配式建筑企业成立的数量，发现企业成立数从2015年来持续保持较高位置。今年受疫情影响，年初成立数量大幅下降，但是近月来新成立企业数量已经恢复到较高水平，同比保持高增'},
            '8':{'content':'根据指数，我们观察到今年我国塔机总体需求量处于持平状态。受疫情影响，上半年的累积12月的地产新开工面积和基建固定资产投资增速下降，但随着国内疫情的缓解和经济活动的修复，房屋新开工面积降幅缩窄、基建投资增速回'},
            '99':{'content':'从指数上看，近年来行业总体景气度持续增加，而增速在19年下半年持续增加，但在20年初出现增速下降，我们认为主要是受疫情影响，导致行业的工作量短期萎缩。截止至10月多维度数据指数同比增长'},
            '110':{'content':'我们根据天眼查的微观数据，统计建筑机械租赁行业企业的情况。我们发现2017年来企业成立数量持续高增长，我们认为主要反映了塔吊从建筑企业自有向租赁市场转变的情况'}
        }     
        result =spectral_cluster(file_content,jobid,cluster_num=3)
        self.result(result,0)
    #-------------------------------------------------------assign condition-----------------
    async def check_conditionassign_post(self,taskid,classname,gid,cname,equal):
        result_data=await conditionPost(taskid,classname,gid,cname)
        print(result_data)
        self.result(result_data,equal)
        return result_data
    #测试指定条件id及条件分组添加条件文本
    async def test_assigncondition_post(self):
        #
        #准备，测试数据
        jobid = str(uuid.uuid1()) 
        cluster_result,group_id =await self.condition_data(jobid,'世界爱数assign')
        #正常添加，
        condid_name={}
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='condi_nameass'+str(i)
            result = await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1
            condid_name[condi_name]=result['cond_id']
        
        jobid2 = str(uuid.uuid1()) 
        #准备，测试数据
        self.text_cluster2(jobid2)
        file_list=['11','1','111','22','333','3','44','555','55','66','77','8','99']
        #conditionAssignPost(taskid,file_list,cond_id,cond_name,group_id)
        #错误返回值测试
        #cond_id错误
        error_result = await conditionAssignPost(jobid2,file_list,'condiderror')
        print(error_result)
        self.result(error_result,1)
        

        #正常
        result = await conditionAssignPost(jobid2,file_list,condid_name['condi_nameass1'])
        print(result)
        self.result(result,0)


        #删除数据
        await self.word_delete(jobid,0)
        await self.word_delete(jobid2,0)
        await self.group_delete(group_id,0)
        time.sleep(2)
        

    #测试相同的文本插入时会返回有相似文本的数据
    async def test_condition_post3(self):
        #准备，测试数据
        jobid = str(uuid.uuid1())    
        cluster_result,group_id =await self.condition_data(jobid,'世界爱数')
        #正常添加，
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='condi_name3'+str(i)
            await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1
   
        jobid2 = str(uuid.uuid1()) 
        #准备，测试数据
        self.text_cluster2(jobid2)
        # task_id.append(jobid2)
        #准备，先添加一个分组，
        json_data = await condiGroupPost("爱数3")
        group_id3 = json_data['group_id']
        self.result(json_data,0)
        #准备，正常task_id 返回正常信息
        json_data = await clusterResultGet(jobid2)
        self.result(json_data,0)
        cluster_result3 = json_data["cluster_result"]
        self.assertTrue(isinstance(cluster_result3, dict))
         
        #正常添加，
        y=1
        for cla_na in list(cluster_result3.keys()):           
            condi_name='condi_name33'+str(y)
            await self.check_condition_post(jobid2,cla_na,group_id3,condi_name,0)         
            y+=1
    
        # return cluster_result,group_id

        #删除数据
        await self.word_delete(jobid,0)
        await self.word_delete(jobid2,0)
        await self.group_delete(group_id,0)
        await self.group_delete(group_id3,0)
        time.sleep(2)
    
    async def check_condition_post(self,taskid,classname,gid,cname,equal):
        result_data=await conditionPost(taskid,classname,gid,cname)
        print(result_data)
        self.result(result_data,equal)
        time.sleep(1)
        return result_data

    async def test_condition_post(self): 
        #准备，测试数据
        jobid = str(uuid.uuid1()) 
        cluster_result,group_id =await self.condition_data(jobid,'全球爱数')
     
        #报错，错误任务id
        tid = '1111111111'
        cname = 'condi_name_error'
        await self.check_condition_post(tid,list(cluster_result.keys())[0],group_id,cname,1)
        #报错，错误分组id
        await self.check_condition_post(jobid,list(cluster_result.keys())[0],'33333','condi_name_error',1)
        #报错，错误类别名称
        await self.check_condition_post(jobid,'error-class',group_id,'condi_name_error',1)
        #正常添加，
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='condi_name4'+str(i)
            await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1
        #重复条件名增加，报错
        result_data=await conditionPost(jobid,list(cluster_result.keys())[0],group_id,'condi_name41')
        self.result(result_data,1)

        #验证，是否添加的条件数量是否正确 ,若添加的条件名都存在说明添加成功  
        conditions = await self.conditon_get()
        cnames=[]
        for cid,cmessage in conditions.items():
            cnames.append(cmessage['cond_name'])
        for o in range(1,i):
            condi_name='condi_name4'+str(o)
            self.assertIn(condi_name,cnames)

        #删除数据
        await self.word_delete(jobid,0)
        await self.group_delete(group_id,0)
        time.sleep(2)
    
    #------------------------------------------condition put-------------
    async def test_condition_put(self):
        #准备，测试数据
        jobid = str(uuid.uuid1()) 
        cluster_result,group_id =await self.condition_data(jobid,'财务')
        #正常添加条件，用于进行下面的修改测试及验证，
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='cw'+str(i)
            await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1    
        #报错，条件id错误，报错
        new_condi_name='condi_name_update'
        result_data=await conditionPut('cond_iderror',new_condi_name)
        self.result(result_data,1)
        #正常，条件id正确，返回正常
        conditions = await self.conditon_get()
        cond_id = list(conditions.keys())[0]
        result_data=await conditionPut(cond_id,new_condi_name)
        self.result(result_data,0)
        
        #重复的条件名报错
        cond_id1 = list(conditions.keys())[1]
        result_data=await conditionPut(cond_id1,new_condi_name)
        self.result(result_data,1)

        #验证，此cond_id对应的name是否修改
        conditions = await self.conditon_get()
        up_name = conditions[cond_id]['cond_name']
        self.assertEqual(new_condi_name,up_name)
        
        #测试下------------------- condition get----------
        #传入错误的id，返回空的
        c_data=await conditionGet(cond_id='1111111')
        self.result(c_data,0)
        #传入正常的id，返回信息
        c_data=await conditionGet(cond_id=cond_id)
        self.result(c_data,0)

        #删除数据
        await self.word_delete(jobid,0)
        await self.group_delete(group_id,0)
        #验证，已没有条件分组数据
        all_cond_data=await conditionGet()
        print("all_cond_data",all_cond_data)
        self.result(all_cond_data,0)
    
    async def conditon_get(self):
        all_cond_data=await conditionGet()
        self.result(all_cond_data,0)
        conditions = all_cond_data['conditions']
        return conditions

    #------------------------------------------condition delete-------------
    #删除条件，
    async def check_condition_delete(self,cond_id,equal):
        result_data=await conditionDelete(cond_id)
        self.result(result_data,equal)
    #删除条件下的文本
    async def check_conditiondoc_delete(self,cond_id,docname,equal):
        result_data=await condidocsDelete(cond_id,docname)
        self.result(result_data,equal)

    
    async def test_condition_delete(self):
        #准备，测试数据
        jobid = str(uuid.uuid1()) 
        cluster_result,group_id =await self.condition_data(jobid,'人事')
        #正常添加条件，用于进行下面的修改测试及验证，
        i=1
        for cla_na in list(cluster_result.keys()):           
            condi_name='condn'+str(i)
            await self.check_condition_post(jobid,cla_na,group_id,condi_name,0)         
            i+=1

        #查询出条件数据，用于测试删除条件及删除条件下的文本   
        conds = await self.conditon_get()
        cond_id=list(conds.keys())[0]
        doc_name = conds[cond_id]['docs'][0]
        #-----------------删除条件下一个文本
        #报错，cond_id 正常，doc_name错误，
        await self.check_conditiondoc_delete(cond_id,'cond_error_name',1) 
        #报错，cond_id 错误，doc_name正常，
        await self.check_conditiondoc_delete('cond_id',doc_name,1)   
        #正常，cond_id 正常，doc_name正常
        await self.check_conditiondoc_delete(cond_id,doc_name,0)
        
        #验证,此条件下的这个文本是否被删除
        conds = await self.conditon_get()
        docs = conds[cond_id]['docs']
        self.assertNotIn(doc_name,docs)

        #-------------------删除条件
        #报错，删除条件，id错误，报错    
        condi_id_error='30553758-bcec-11ea-853d'
        await self.check_condition_delete(condi_id_error,1)
        #正确，删除条件，id正确
        await self.check_condition_delete(cond_id,0)
        #
        #验证，查看此条件是否被删除
        conds = await self.conditon_get()
        cids = list(conds.keys())
        self.assertNotIn(cond_id,cids)

        #删除数据
        await self.word_delete(jobid,0)
        await self.group_delete(group_id,0)
        time.sleep(2)

        #验证，已没有条件分组数据
        all_cond_data=await conditionGet()
        self.result(all_cond_data,0)
      

    #------------------------------------------group delete-------------
    async def group_delete(self,gid,equal):
        json_data = await condiGroupDelete(gid)
        self.result(json_data,equal)

    async def test_group_delete(self):
        #删除条件分组,传入错误参数
        group_id='2748afa0-bc42-11ea-b228-005056'
        await self.group_delete(group_id,1)
        time.sleep(1)
        
    #------------------------------------------word delete-------------
    async def word_delete(self,tid,eq):
        json_data = await docsWordsDelete(tid)
        self.result(json_data,eq)

    async def test_word_delete(self):
        #错误task-id 返回错误信息
        tid = '1111111'
        await self.word_delete(tid,1)
    

    def test_word_wextract(self):
        args = ('cshi','默认为恢复至原客户端原位置注意：此处可以选择恢复至其他位置')
        dn,ky = extract_(args)
        print(dn,ky)
        self.assertIsInstance(dn,str)
        self.assertIsInstance(ky,str)

        args = ('cshi','位置')
        dn,ky = extract_(args)
        print(dn,ky)
        self.assertEqual(dn,None)
        self.assertEqual(ky,None)
    # def test_milvus_client(self):
    #     from auto_text_filter.milvus_client import AioMilvus
    #     import asyncio
    #     collection_name ='atf_ce'
        

    #     milvus_client = AioMilvus(asyncio.get_event_loop(), collection_name)
    #     #传教partition报错
    #     milvus_cre_p = milvus_client.creat_partition('tt')
    #     self.result(milvus_cre_p,1)
    #     #miluvs 插入向量报错
    #     import numpy as np
    #     # import random
    #     vec=np.random.randn(1,10)
    #     v= vec.reshape(1,-1)
    #     milvus_insert = milvus_client.insert(v,'tt')
    #     self.result(milvus_insert,1)
    #     #删除partition报错
    #     milvus_drop_p = milvus_client.drop_partition('tt')
    #     self.result(milvus_drop_p,1)
        
    #     #测试创建一个collection，
    #     from read_config import milvus_config
    #     from milvus import Milvus, IndexType, MetricType, Status
    #     import asyncio
    #     milvus = Milvus(host=milvus_config["host"], port=milvus_config["port"])
    #     param = {
    #             'collection_name': collection_name, 
    #             'dimension': 100, 
    #             'index_file_size': 1024, 
    #             'metric_type': MetricType.IP
    #         }
    #     milvus.create_collection(param)

    #     ivf_param = {"m": 64, "nlist": 1000}
    #     milvus.create_index(collection_name, IndexType.IVF_PQ, ivf_param)
    #     print("创建成功")

    #     ress = milvus.create_partition(collection_name,'tt')
    #     print(ress)
    #     self.result(ress,0)
    #     #报错，向量长度不一致
    #     milvus_insert = milvus_client.insert(v,'tt')
    #     self.result(milvus_insert,1)
    #     #删除collection
    #     result_dropc = milvus.drop_collection(collection_name)
    #     self.result(result_dropc,0)






if __name__ == "__main__":
    unittest.main()
