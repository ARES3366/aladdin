# _*_ coding:utf-8 _*_

import sys,os
import json
import urllib
import requests
import numpy as np

class ClassiffierModelEvaluator():
    def __init__(self, num_label=2, label_name_list=None):
        self.num_label=num_label
        self.sts = np.zeros([num_label,num_label],dtype=np.int32)
        self.label_name_list = label_name_list if label_name_list else ['cls_%s'%i for i in range(num_label)]
        self.quota=None

    def add(self,r, c):
        self.sts[r,c] += 1

    def batch_add(self, all_label):
        for r,c in all_label:
            self.sts[r,c] += 1

    def update_quota(self):
        if not self.label_name_list:
            self.label_name_list=[range(self.sts.shape[0])]
        sum_r = np.sum(self.sts,axis=1)
        sum_c = np.sum(self.sts,axis=0)
        quota = np.zeros([3, self.num_label],dtype=np.float)
        rows, cols = self.sts.shape
        for c in range(cols):
            quota[0,c] = self.sts[c,c] / sum_r[c]
            quota[1,c] = self.sts[c,c] / sum_c[c]
        quota[2] = quota[0] * quota[1] * 2 / (quota[0] + quota[1])
        macro_avg = np.mean(quota,axis=1)
        macro_avg = np.reshape(macro_avg,[3,1])
        micro_avg = np.ones([3,1]) * np.trace(self.sts) / np.sum(self.sts) #矩阵的迹/矩阵所有元素之和
        quota = np.concatenate([quota, macro_avg,micro_avg], axis=1)
        self.quota = np.around(quota, decimals=4)

    def __str__(self):
        from prettytable import PrettyTable
        table = PrettyTable(['真实标签\预测标签'] + self.label_name_list + ['宏平均','微平均'])
        for r in range(self.num_label):
            table.add_row([self.label_name_list[r]]+list(self.sts[r])+['/', '/'])
        table.add_row(['召回率']+list(self.quota[0]))
        table.add_row(['精确率']+list(self.quota[1]))
        table.add_row(['F1值']+list(self.quota[2]))
        return str(table)

    def readfiles(self, path):
        files = os.listdir(path) #得到文件夹下的所有文件名称  
        s = []  
        for file in files: 
            if not os.path.isdir(file): 
                f = open(path+"/"+file) 
                str = f.read() 
                s.append(str) #每个文件的文本存到list中
                f.close
        return s

    def batch_classify(self, list):
        length = len(list)
        results = []
        num = int(length/100)
        if length%100 == 0:
            for i in range(num):
                j = 0
                content = list[j:j+100]
                j += 100
                request = "http://localhost:32032/analysis/text/batch_common_classify"
                data = {"content_list":content}
                result = requests.post(request, json=data, verify=False)
                result = json.loads(result.content)
                labels = result["label_list"]
                for n in range(len(labels)):
                    results.append(labels[n])
        else:
            for i in range(num):
                j = 0
                content = list[j:j+100]
                j += 100
                request = "http://localhost:32032/analysis/text/batch_common_classify"
                data = {"content_list":content}
                result = requests.post(request, json=data, verify=False)
                result = json.loads(result.content)
                labels = result["label_list"]
                for n in range(len(labels)):
                    results.append(labels[n])
            content1 = list[(length-length%100):length]
            request1 = "http://localhost:32032/analysis/text/batch_common_classify"
            data1 = {"content_list":content1}
            result1 = requests.post(request1, json=data1, verify=False)
            result2 = json.loads(result1.content)
            labels1 = result2["label_list"]
            for n in range(len(labels1)):
                results.append(labels[n])
        return results

if __name__=='__main__':
    classify = ClassiffierModelEvaluator(num_label=14,label_name_list=['体育','娱乐','家居','彩票','房产','教育','时尚','时政','星座','游戏','社会','科技','股票','财经'])
    #dic = {"房产":4,"时尚":6,"星座":8,"游戏":9,"社会":10,"财经":13}
    dic = {"股票":12,"财经":13,"体育":0,"娱乐":1,"家居":2,"彩票":3,"房产":4,"教育":5,"时尚":6,"时政":7,"星座":8,"游戏":9,"社会":10,"科技":11}
    for k,v in dic.items():
        filelist = classify.readfiles("/data/THUCNewsTest/%s" % k)
        label_list = classify.batch_classify(filelist)
        for item in label_list:
            classify.add(v,dic[item])
        classify.update_quota()
        print(classify)
