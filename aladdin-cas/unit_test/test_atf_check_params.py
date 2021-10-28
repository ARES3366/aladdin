#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest
from auto_text_filter import atf_params_check 

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

#===================================================  参数判断 单条件 ==========
    
class TestParamsCheck(unittest.TestCase):
    #-------------------------- word  post ---------------
    #参数检查
    def check_word_post_params(self,params,equal):
        result = atf_params_check.word_post(params)
        print(result)
        self.assertEqual(equal,result['status'])
    def test_word_post(self):
        #请求参数为非dict
        params=[]
        self.check_word_post_params(params,1)
        #请求参数为空
        params={}
        self.check_word_post_params(params,1)
        #参数中contents没有元素
        params={"contents":{}}
        self.check_word_post_params(params,1)
        #缺少contents参数
        params={"cluster_num":3}
        self.check_word_post_params(params,1)
        #contents没有数据
        params={"contents":{},"cluster_num":3}
        self.check_word_post_params(params,1)
        #contents的类型错误
        params={"contents":[],"cluster_num":3}
        self.check_word_post_params(params,1)
        #contents数量少于10个
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"}
                             },"cluster_num":3}
        self.check_word_post_params(params,1)
         #clust_num小于2
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":1}
        self.check_word_post_params(params,1)
        #doc_name 为空字符串
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
        #content值为空string
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":""},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
        #content值为非string
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":144411},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
        #cluster_num 大于contents长度
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":13}
        self.check_word_post_params(params,1)
    
        #cluster_num为非int类型
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":"3"}
        self.check_word_post_params(params,1)
        #缺少cluster_num
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}}}
        self.check_word_post_params(params,0)
        #缺少content
        params={"contents":{"a":{},
                           "b":{},
                           "c":{},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
        #doc_name 为非字符串
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           3:{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
    #doc_name 为None
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           None:{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
        #content值为None
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":None},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        self.check_word_post_params(params,1)
        #参数cluster_num为None
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":'ffffff'},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}
                           },
                "cluster_num":None}
        self.check_word_post_params(params,1)
        #参数contents多与200
        conts={}
        for i in range(1001):
            dname = 'doc'+str(i)
            cont = 'cont'+str(i)
            ct={'content':cont}
            conts[dname]=ct
        params={'contents':conts,'cluster_num':3}
        self.check_word_post_params(params,1)
        #cod name大于128
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":'ffffff'},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa"*65:{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}
                           },
                "cluster_num":3}
        self.check_word_post_params(params,1)
        #cod name有特殊字符
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":'ffffff'},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "a/a":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}
                           },
                "cluster_num":3}
        self.check_word_post_params(params,1)
        #cod name有特殊字符
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":'ffffff'},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "c*a":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}
                           },
                "cluster_num":3}
        self.check_word_post_params(params,1)
        #参数正常
        params={"contents":{"a":{"content":"111"},
                           "b":{"content":"311"},
                           "c":{"content":'ffffff'},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}
                           },
                "cluster_num":3}
        self.check_word_post_params(params,0)
    #content长度大于10000，返回的content为截取的10000
    def test_word_post10000(self):
        params={"contents":{"a":{"content":"111"*4000},
                           "b":{"content":"311"},
                           "c":{"content":"3311"},
                           "d":{"content":"144411"},
                           "e":{"content":"14441"},
                           "f":{"content":"1555511"},
                           "aa":{"content":"13311"},
                           "ba":{"content":"31331"},
                           "ca":{"content":"333311"},
                           "da":{"content":"14433411"},
                           "ea":{"content":"33333"},
                           "fa":{"content":"153355511"}},"cluster_num":3}
        
        result = atf_params_check.word_post(params)
        # print(result)
        self.assertEqual(10000,len(result['contents']['a']['content']))



    #------------------------------ word get ---------------
    def check_word_get_params(self,taskid,equal_num):
        result = atf_params_check.word_get_delete(taskid)
        print(result)
        self.assertEqual(equal_num,result['status'])
    
    def test_word_get(self):
        #查询分析结果，id类型错误
        taskid=['1']
        self.check_word_get_params(taskid,1)
        #id为none
        taskid=None
        self.check_word_get_params(taskid,1)
        #id为none
        taskid='     '
        self.check_word_get_params(taskid,1)
        #id为正常
        taskid='None'
        self.check_word_get_params(taskid,0)
    
    #------------------------------ word delete ---------
    def check_word_delete_params(self,taskid,equal_num):
        result = atf_params_check.word_get_delete(taskid)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_word_delete(self):
        #删除分析结果，传入错误任务id，非string
        taskid=['1']
        self.check_word_delete_params(taskid,1)
        #删除分析结果，id为None，报错
        taskid=None
        self.check_word_delete_params(taskid,1)
        #id为'         '
        taskid='       '
        self.check_word_delete_params(taskid,1)
        #id为正常
        taskid='None'
        self.check_word_delete_params(taskid,0)

    #------------------------------ word put -----------
    def check_word_put_params(self,params,equal_num):
        result = atf_params_check.word_put(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_word_put_params(self):
        #参数为{}
        params = {}
        self.check_word_put_params(params,1)
        #参数为[]
        params = []
        self.check_word_put_params(params,1)
        #taskid.strip()=0
        params = {"taskid":'    ',"doc_name":'tt',"action":0}
        self.check_word_put_params(params,1)
        #taskid.strip()=0
        params = {"taskid":'22 ',"doc_name":'    ',"action":0}
        self.check_word_put_params(params,1)
        #缺少action
        params = {"taskid":'111',"doc_name":'tt'}
        self.check_word_put_params(params,1)
        #缺少doc_name
        self.check_word_put_params(params,1)
        #缺少taskid
        params = {"doc_name":'tt',"action":0}
        self.check_word_put_params(params,1)
        #taskid为非string
        params = {"taskid":111,"doc_name":'tt',"action":0}
        self.check_word_put_params(params,1)
        #action为非int
        params = {"taskid":'111',"doc_name":'tt',"action":'0'}
        self.check_word_put_params(params,1)
        #doc_name为非string
        params = {"taskid":'111',"doc_name":['1'],"action":0}
        self.check_word_put_params(params,1)
        #taskid为None
        params = {"taskid":None,"doc_name":'tt',"action":0}
        self.check_word_put_params(params,1)
        #action为None
        params = {"taskid":'111',"doc_name":'tt',"action":None}
        self.check_word_put_params(params,1)
        #doc_name 为None
        params = {"taskid":'111',"doc_name":None,"action":0}
        self.check_word_put_params(params,1)
        #参数正常
        params = {"taskid":'111',"doc_name":'None',"action":0}
        self.check_word_put_params(params,0)

    #------------------------------ group post -----------
    #
    def check_group_post_params(self,params,equal_num):
        result = atf_params_check.group_post(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_group_post(self):

        #参数为{}
        params = {}
        self.check_group_post_params(params,1)
        #参数为[]
        params = []
        self.check_group_post_params(params,1)
        #分组名称为None
        params = {'group_name':None}
        self.check_group_post_params(params,1)
        #分组名称为None
        params = {'group_name':'    '}
        self.check_group_post_params(params,1)
        #分组名称为非string
        params = {'group_name':12}
        self.check_group_post_params(params,1)
        ##分组名称包含特殊字符
        params = {'group_name':'1/2'}
        self.check_group_post_params(params,1)
        ##分组名称包含特殊字符
        params = {'group_name':'1aaa|2'}
        self.check_group_post_params(params,1)
        ##分组名称包含特殊字符
        params = {'group_name':'1aaa*2'}
        self.check_group_post_params(params,1)
        #分组名称超过128个字符
        params = {'group_name':'aaa'*43}
        self.check_group_post_params(params,1)
        #分组名称正常
        params = {'group_name':'    aaa    '}
        print(params)
        self.check_group_post_params(params,0)
        #分组名称正常
        params = {'group_name':'aaa'}
        self.check_group_post_params(params,0)

    #------------------------------ group put--------0---------
    def check_group_put_params(self,params,equal_num):
        result = atf_params_check.group_put(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_group_put(self):
        #参数为{}
        params = {}
        self.check_group_put_params(params,1)
        #参数为[]
        params = []
        self.check_group_put_params(params,1)
        #参数中group_id '     '
        params = {'group_id':'        ','group_name':'aaa'}
        self.check_group_put_params(params,1)
        #参数中group_id 非string
        params = {'group_id':123,'group_name':'aaa'}
        self.check_group_put_params(params,1)
        #参数中group_id 为None
        params = {'group_id':None,'group_name':'aaa'}
        self.check_group_put_params(params,1)
        #参数中分组名称没有group_name
        params = {'group_id':'123'}
        self.check_group_put_params(params,1)
        #group_name 为’   ‘
        params = {'group_id':'123','group_name':'          '}
        self.check_group_put_params(params,1)
        #参数中分组名称非string
        params = {'group_id':'123','group_name':['aaa']}
        self.check_group_put_params(params,1)
        #参数中分组名称为None
        params = {'group_id':'123','group_name':None}
        self.check_group_put_params(params,1)
        #参数中分组名称包含特殊字符
        params = {'group_id':'123','group_name':'No"ne'}
        self.check_group_put_params(params,1)
        #参数中分组名称包含特殊字符
        params = {'group_id':'123','group_name':'No?ne'}
        self.check_group_put_params(params,1)
        #参数中分组名称包含特殊字符
        params = {'group_id':'123','group_name':'No:ne'}
        self.check_group_put_params(params,1)
        #参数中分组名称长度超过128个字符
        params = {'group_id':'123','group_name':'None'*33}
        self.check_group_put_params(params,1)
        #参数正常
        params = {'group_id':'123','group_name':'    None    '}
        self.check_group_put_params(params,0)
        #参数正常
        params = {'group_id':'123','group_name':'None'}
        self.check_group_put_params(params,0)

    #------------------------------ group get---------0--------
    def check_group_get_params(self,group_id,equal_num):
        result = atf_params_check.group_get(group_id)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_group_get(self):
        #参数group_id 为非string
        group_id = 123
        self.check_group_get_params(group_id,1)
        #参数group_id 为非string
        group_id = ['123']
        self.check_group_get_params(group_id,1)
        #参数group_id 为'   '
        group_id = '   '
        self.check_group_get_params(group_id,1)
        #参数group_id 为string
        group_id = '123'
        self.check_group_get_params(group_id,0)
    def check_group_onlyget_params(self,only,equal_num):
        result = atf_params_check.group_only_get(only)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_group_onlyget(self):
        #参数group_id 为None
        group_id = None
        self.check_group_onlyget_params(group_id,1)
        #参数group_id 为非string
        group_id = 123
        self.check_group_onlyget_params(group_id,1)
        #参数group_id 为非string
        group_id = ['123']
        self.check_group_onlyget_params(group_id,1)
        #参数group_id 为string 
        group_id = '1'
        self.check_group_onlyget_params(group_id,0)
        #不是'0'或'1'报错
        group_id = '3'
        self.check_group_onlyget_params(group_id,1)
        #参数group_id 为string
        group_id = '0'
        self.check_group_onlyget_params(group_id,0)
        #不是'0'或'1'报错
        group_id = '10'
        self.check_group_onlyget_params(group_id,1)

    #------------------------------ group delete------0--------
    def check_group_delete_params(self,group_id,equal_num):
        result = atf_params_check.group_delete(group_id)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_group_delete(self):
        #参数group_id 为'   '
        group_id = '   '
        self.check_group_delete_params(group_id,1)
        #参数group_id 为非string
        group_id = 123
        self.check_group_delete_params(group_id,1)
        #参数group_id 为非string
        group_id = [123]
        self.check_group_delete_params(group_id,1)
        #参数group_id 为None
        group_id = None
        self.check_group_delete_params(group_id,1)
        #参数group_id 正常
        group_id = 'None'
        self.check_group_delete_params(group_id,0)

    #------------------------------ condition post -----------
    def check_condition_post_params(self,params,equal_num):
        result = atf_params_check.condition_post(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_condition_post(self):
        #参数为{}
        params={}
        self.check_condition_post_params(params,1)
        #参数为[]
        params=[]
        self.check_condition_post_params(params,1)
        #参数中缺少task-id':
        params={'class_name':'ccc','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #参数中缺少class_name
        params={'taskid':'111','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #缺少group_id
        params={'taskid':'111','class_name':'ccc','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #缺少condition_name
        params={'taskid':'111','class_name':'ccc','group_id':'ggg'}
        self.check_condition_post_params(params,1)
        #task_id为非string
        params={'taskid':111,'class_name':'ccc','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #task_id 为None
        params={'taskid':None,'class_name':'ccc','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #class_name 为非string
        params={'taskid':'111','class_name':['dd'],'group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #class_name 为None
        params={'taskid':'111','class_name':None,'group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #group_id 为非string
        params={'taskid':'111','class_name':'ccc','group_id':['ggg'],'cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #group_id 为None
        params={'taskid':'111','class_name':'ccc','group_id':None,'cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #condition_name 为非string
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':['cond']}
        self.check_condition_post_params(params,1)
        #condition——name 为None
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':None}
        self.check_condition_post_params(params,1)
        #condition_name 包含特殊字符
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'c<ond'}
        self.check_condition_post_params(params,1)
        #condition_name 包含特殊字符
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'c>ond'}
        self.check_condition_post_params(params,1)
        #condition_name 包含特殊字符
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'c\\ond'}
        self.check_condition_post_params(params,1)
        #condition_name 包含特殊字符
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'c:ond'}
        self.check_condition_post_params(params,1)
        #condition_name 长度超过128 
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'cond'*33}
        self.check_condition_post_params(params,1)
        #taksid为 '     '
        params={'taskid':'       ','class_name':'ccc','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #classname '      '
        params={'taskid':'111','class_name':'      ','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #group_i为'  '
        params={'taskid':'111','class_name':'ccc','group_id':'   ','cond_name':'cond'}
        self.check_condition_post_params(params,1)
        #cond_name 为  '        '
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'       '}
        self.check_condition_post_params(params,1)
        #参数正常,修改cond_name
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'    cond    '}
        print(params)
        self.check_condition_post_params(params,0)
        #参数正常
        params={'taskid':'111','class_name':'ccc','group_id':'ggg','cond_name':'cond'}
        self.check_condition_post_params(params,0)
    
    #------------------------------ assign condition post -----------
    def check_assigncondition_post_params(self,params,equal_num):
        result = atf_params_check.conditionAssign_post(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_assigncondition_post(self):
        #taskid,file_list,cond_id,cond_name,group_id
        #'taskid'  'file_list' 'cond_id' 'group_id'  'cond_name' 
        #参数为{}
        params={}
        self.check_assigncondition_post_params(params,1)
        #参数为[]
        params=[]
        self.check_assigncondition_post_params(params,1)
        #参数中缺少task-id':
        params={'file_list':['t1'],'cond_id':'123'}
        self.check_assigncondition_post_params(params,1)
        #参数中缺少file_list
        params={'taskid':'111','cond_id':'123'}
        self.check_assigncondition_post_params(params,1)
        
        #缺少condition_id
        params={'taskid':'111','file_list':['t1']}
        self.check_assigncondition_post_params(params,1)
        #task_id为非string
        params={'taskid':111,'file_list':['t1'],'cond_id':'123'}
        self.check_assigncondition_post_params(params,1)
        #task_id 为None
        params={'taskid':None,'file_list':['t1'],'cond_id':'123'}
        self.check_assigncondition_post_params(params,1)
        #task_id 为''
        params={'taskid':'','file_list':['t1'],'cond_id':'123'}
        self.check_assigncondition_post_params(params,1)
        #cond_id 为非string
        params={'taskid':'111','file_list':['t1'],'cond_id':123}
        self.check_assigncondition_post_params(params,1)
        #cond_id 为None
        params={'taskid':'111','file_list':['t1'],'cond_id':None}
        self.check_assigncondition_post_params(params,1)
        #cond_id 为''
        params={'taskid':'111','file_list':['t1'],'cond_id':''}
        self.check_assigncondition_post_params(params,1)
        
        #taskid 为'    '
        params={'taskid':'    ','file_list':['t1'],'cond_id':'123','cond_name':'tt','group_id':'333'}
        self.check_assigncondition_post_params(params,1)
        #cond_id 为'    '
        params={'taskid':'111','file_list':['t1'],'cond_id':'   ','cond_name':'tt','group_id':'333'}
        self.check_assigncondition_post_params(params,1)
        #file_list为非list
        params={'taskid':'111','file_list':'t1','cond_id':'123','cond_name':'ttt','group_id':'gg33'}
        self.check_assigncondition_post_params(params,1)
        #file_list为非list
        params={'taskid':'111','file_list':123,'cond_id':'123','cond_name':'ttt','group_id':'gg33'}
        self.check_assigncondition_post_params(params,1)
        #file_list为空
        params={'taskid':'111','file_list':[],'cond_id':'123','cond_name':'ttt','group_id':'gg33'}
        self.check_assigncondition_post_params(params,1)
        #file_list的元素为None
        params={'taskid':'111','file_list':[None],'cond_id':'123','cond_name':'ttt','group_id':'gg33'}
        self.check_assigncondition_post_params(params,1)
        #file_list的元素为非string
        params={'taskid':'111','file_list':[113,223],'cond_id':'123','cond_name':'ttt','group_id':'gg33'}
        self.check_assigncondition_post_params(params,1)
        #file_list的元素为空
        params={'taskid':'111','file_list':['','111'],'cond_id':'123','cond_name':'ttt','group_id':'gg33'}
        self.check_assigncondition_post_params(params,1)

        #参数正常,修改cond_name
        params={'taskid':'111','file_list':['t1'],'cond_id':'123'}
        print(params)
        self.check_assigncondition_post_params(params,0)
        #参数正常
        params={'taskid':'111','file_list':['t1'],'cond_id':'123'}
        self.check_assigncondition_post_params(params,0)

    #------------------------------ condition put--------0-----
    def check_condition_put_params(self,params,equal_num):
        result = atf_params_check.condition_put(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_condition_put(self):
        #参数为{}
        params={}
        self.check_condition_put_params(params,1)
        #参数为[]
        params=[]
        self.check_condition_put_params(params,1)
        #参数缺少cond_id
        params={'cond_name':'aa'}
        self.check_condition_put_params(params,1)
        #参数缺少cond_name
        params={'cond_id':'1'}
        self.check_condition_put_params(params,1)
        #cond_id 为非string
        params={'cond_id':1,'cond_name':'aa'}
        self.check_condition_put_params(params,1)
        #cond_id 为None
        params={'cond_id':None,'cond_name':'aa'}
        self.check_condition_put_params(params,1)
        #cond_name 为非string
        params={'cond_id':'1','cond_name':12}
        self.check_condition_put_params(params,1)
        #cond_name 为none
        params={'cond_id':'1','cond_name':None}
        self.check_condition_put_params(params,1)
        #cond_name 包含特殊字符
        params={'cond_id':'1','cond_name':'a,a'}
        self.check_condition_put_params(params,1)
        #cond_name 包含特殊字符
        params={'cond_id':'1','cond_name':'a:a'}
        self.check_condition_put_params(params,1)
        #cond_name 包含特殊字符
        params={'cond_id':'1','cond_name':'a"a'}
        self.check_condition_put_params(params,1)
        #cond_name 长度大于128
        params={'cond_id':'1','cond_name':'aa'*65}
        self.check_condition_put_params(params,1)
        #cond_id为 '    '
        params={'cond_id':'    ','cond_name':'cccc'}
        self.check_condition_put_params(params,1)
        #cond_name '    '
        params={'cond_id':'aa','cond_name':'   '}
        self.check_condition_put_params(params,1)
        #正常参数.修改名字
        params={'cond_id':'aa','cond_name':'         cccc           '}
        print(params)
        self.check_condition_put_params(params,0)
        #正常参数
        params={'cond_id':'aa','cond_name':'cccc'}
        self.check_condition_put_params(params,0)
    #------------------------------ condition get-------0------
    def check_condition_get_params(self,cond_id,equal_num):
        result = atf_params_check.condition_get(cond_id)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_condition_get(self):
        #cond_id 为非sring
        cond_id={'cond_id':'1'}
        self.check_condition_get_params(cond_id,1)
        #cond_id 为非sring
        cond_id=['1']
        self.check_condition_get_params(cond_id,1)
        #cond_od=''
        cond_id=''
        self.check_condition_get_params(cond_id,1)
        #cond_id 正常
        cond_id='123'
        self.check_condition_get_params(cond_id,0)

    #------------------------------ condition delete-----0-----
    def check_condition_delete_params(self,cond_id,equal_num):
        result = atf_params_check.condition_delete(cond_id)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def check_condition_doc_delete_params(self,doc_name,equal_num):
        result = atf_params_check.condition_delete_docname(doc_name)
        print(result)
        self.assertEqual(equal_num,result['status'])
    def test_condition_delete(self):
        #cond_id 为非sring
        cond_id={'cond_id':'1'}
        self.check_condition_delete_params(cond_id,1)
        #cond_id 为非sring
        cond_id=['1']
        self.check_condition_delete_params(cond_id,1)
        #cond_id 为None
        cond_id=None
        self.check_condition_delete_params(cond_id,1)
        #cond_id 为''
        cond_id=''
        self.check_condition_delete_params(cond_id,1)
        #cond_id 为正常
        cond_id='12'
        self.check_condition_delete_params(cond_id,0)
        #cond-id正常，doc_name 为非string
        doc_name=['None']
        self.check_condition_doc_delete_params(doc_name,1)
        #cond-id正常，doc_name 为''
        doc_name=' '
        self.check_condition_doc_delete_params(doc_name,1)
        #cond-id正常，doc_name 为'33'正常
        doc_name='33'
        self.check_condition_doc_delete_params(doc_name,0)
    
    #------------------------------ text_filter -------0---
    def check_text_filter_post(self,params,equal_num):
        result = atf_params_check.filter_params_check(params)
        print(result)
        self.assertEqual(equal_num,result['status'])
    
    def test_text_filter_post1(self):
        #参数为{}
        params={}
        self.check_text_filter_post(params,1)
        #参数为[]
        params=[]
        self.check_text_filter_post(params,1)
        #参数中缺少content
        params={'condition':['1']}
        self.check_text_filter_post(params,1)
        #content 非string 
        params={'content':11,'condition':['1']}
        self.check_text_filter_post(params,1)
        #content 非string 
        params={'content':None,'condition':['1']}
        self.check_text_filter_post(params,1)
        #content 为空
        params={'content':'','condition':['']}
        self.check_text_filter_post(params,1)
        #cond_id_list 非list
        params={'content':'11','condition':'11'}
        self.check_text_filter_post(params,1)
        # cond_id 为非string
        params={'content':'11','condition':[1,2]}
        self.check_text_filter_post(params,1)
        # cond_id 为空
        params={'content':'11','condition':[]}
        self.check_text_filter_post(params,0)
        # cond_id 为None
        params={'content':'11','condition':[None,2]}
        self.check_text_filter_post(params,1)
        # cond_id 为''
        params={'content':'11','condition':['','1']}
        self.check_text_filter_post(params,1)
        #condition list 超过100个报错
        cod = [str(i) for i in range(101)]
        params={'content':'11','condition':cod}
        self.check_text_filter_post(params,1)
        # 正常
        params={'content':'11','condition':['123','441']}
        self.check_text_filter_post(params,0)

    # content 长度大于10000，截取的长度为10000，正常返回，
    def test_text_filter_post128(self):
        params={'content':'aaa'*4000,'condition':['1']}
        result = atf_params_check.filter_params_check(params)
        # print(result)
        self.assertEqual(10000,len(result['params']['content']))
    
    #-----------------------------------------textfilter_analysis------------
    def check_textfilter_analysis_post(self,params,equal_num):
        result = atf_params_check.filter_analysis_check(params)
        print(result)
        self.assertEqual(equal_num,result['status'])

    def test_textfilter_analysis(self):
        #参数为{}
        params={}
        self.check_textfilter_analysis_post(params,1)
        #参数为[]
        params=[]
        self.check_textfilter_analysis_post(params,1)
        #参数缺少content
        params = {
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #参数缺少condition
        params = {
        'content': "string",
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #参数缺少expect_cond_id
        params = {
        'content': "string",
        'condition': ['cond_id1','cond_id2']
        }
        self.check_textfilter_analysis_post(params,1)
        #content 非string 
        params = {
        'content': 123,
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #content None 
        params = {
        'content': None,
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #content 为空
        params = {
        'content': "   ",
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #condition为非list
        params = {
        'content': "string",
        'condition': {'cond_id1':12,'cond_id2':23},
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #condition为非list
        params = {
        'content': "string",
        'condition': 'cond_id1',
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #condition中为空
        params = {
        'content': "string",
        'condition': [],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,0)
        #condition的值有None
        params = {
        'content': "string",
        'condition': ['cond_id1',None],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #condition中的值有空
        params = {
        'content': "string",
        'condition': ['cond_id1','  '],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #condition中的值有非string
        params = {
        'content': "string",
        'condition': ['cond_id1',123],
        'expect_cond_id':'cond_id1'
        }
        self.check_textfilter_analysis_post(params,1)
        #expect_cond_id的值为非string
        params = {
        'content': "string",
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':['cond_id1']
        }
        self.check_textfilter_analysis_post(params,1)
        #expect_cond_id的值为None
        params = {
        'content': "string",
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':None
        }
        self.check_textfilter_analysis_post(params,1)
        #expect_cond_id 的值为空字符串
        params = {
        'content': "string",
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'  '
        }
        self.check_textfilter_analysis_post(params,1)
        #正常
        params = {
        'content': "string",
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'expectid'
        }
        self.check_textfilter_analysis_post(params,0)

    # content 长度大于10000，截取的长度为10000，正常返回，
    def test_textfilter_analysis_post10000(self):
        params = {
        'content': "string"*20000,
        'condition': ['cond_id1','cond_id2'],
        'expect_cond_id':'expectid'
        }
        result = atf_params_check.filter_analysis_check(params)
        # print(result)
        self.assertEqual(10000,len(result['params']['content']))    

        
   

if __name__ == "__main__":
    unittest.main()
