# -*- conding:utf-8 -*-
from collections import defaultdict
import os
import unittest
import time
import json


class Search(object):
    def __init__(self):
        pass
    def search_doc(self,fingerprint):
        target = fingerprint["target_doc"]
        fingerprint_db = fingerprint["fingerprint_db"]
        #整理指纹数据库，存入map中，可供查询
        map1 = defaultdict(list)
        map2 = defaultdict(list)
        map3 = defaultdict(list)
        map4 = defaultdict(list)
        idmap = {}
        for key, val in fingerprint_db.items():
            map1[val[0]].append(key)
            map2[val[1]].append(key)
            map3[val[2]].append(key)
            map4[val[3]].append(key)
            idmap[key] = val[4]
        #遍历目标指纹数据，并在指纹数据库中搜索相同或相似的文本
        tar_message={}
        for tar in target.keys():
            tar_fp = target[tar]
            tarfp1,tarfp2,tarfp3,tarfp4,tarfp = tar_fp[0],tar_fp[1],tar_fp[2],tar_fp[3],tar_fp[4]
            #定义一个列表存与这个目标文件疑似相同或相似的文本id
            nameset=[]
            if tarfp1 in map1.keys():
                onelist = map1[tarfp1]
                nameset.extend(onelist)
            if tarfp2 in map2.keys():
                twolist = map2[tarfp2]
                nameset.extend(twolist)
            if tarfp3 in map3.keys():
                threelist = map3[tarfp3]
                nameset.extend(threelist)
            if tarfp4 in map4.keys():
                fourlist = map4[tarfp4]
                nameset.extend(fourlist)
            namesets = set(nameset)
            #定义一个列表存精确对比后的相同或相似的文本
            dbid = []
            if len(namesets) == 0:
                tar_message[tar]=dbid
                continue
            else:
                for name in namesets:
                    namefp = idmap[name]
                    dis = self.distance(namefp,tarfp)
                    if dis<=3:
                        dbid.append(name)
                tar_message[tar]=dbid
        return tar_message
    def distance(self,simhashcode1,simhashcode2):
        yihuo = simhashcode1 ^ simhashcode2
        dis = bin(yihuo).count("1")
        return dis 



