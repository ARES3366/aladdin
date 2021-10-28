# -*- conding:utf-8 -*-
import jieba
import jieba.analyse
import numpy as np
import time
import os
import struct

class Simhash(object):
    def __init__(self):
        pass

    def __str__(self):
        return str
    def keywords(self,content):
        keywords = jieba.analyse.extract_tags(content, topK=30, withWeight=True, allowPOS=('n', 'nr','nt','ns','v','vn'))
        return keywords
    
    def simhash(self,content):
        #print("content_length:%s"%(len(content)))
        #keyword = jieba.analyse.extract_tags(content, topK=30, withWeight=True, allowPOS=('n', 'nr','nt','ns','v','vn'))
        keyword = self.keywords(content)
        hash_list =[]
        if len(keyword)==0:
            return "" 
        for word,weight in keyword:
            weight = int(weight*100)
            word_hash = self.word_to_hash(word)
            temp=[]
            for i in word_hash:
                if i=='1':
                    temp.append(weight)
                else:
                    temp.append(-weight)
            hash_list.append(temp)
        list_total=np.sum(np.array(hash_list),axis=0)
        
        a=0
        for i,v in enumerate(list_total):
            if v>=0:
                a =a<<1
                a=a+1
            else:
                a=a<<1
        return str(a)
    def simhash_noPOS(self,content):
        #print("content_length:%s"%(len(content)))
        keyword = jieba.analyse.extract_tags(content, topK=30, withWeight=True)
        
        hash_list =[]
        for word,weight in keyword:
            weight = int(weight*100)
            word_hash = self.word_to_hash(word)
            temp=[]
            for i in word_hash:
                if i=='1':
                    temp.append(weight)
                else:
                    temp.append(-weight)
            hash_list.append(temp)
        list_total=np.sum(np.array(hash_list),axis=0)

        a=0
        for i,v in enumerate(list_total):
            if v>=0:
                a =a<<1
                a=a+1
            else:
                a=a<<1
        return str(a) 
    def word_to_hash(self,word):
        try:
            while len(word) < 3:
                word = word +word[0]
            x = ord(word[0]) << 7
            m = 1000003
            mask = 2 ** 128 - 1
            for c in word:
                x = ((x * m) ^ ord(c)) & mask
            x ^= len(word)
            if x == -1:
                x = -2
            x = bin(x).replace('0b', '').zfill(64)[-64:]
            return str(x)
        except:
            print('Error! can\'t convert to hashcode')

