#!/usr/bin/env python
# -*- coding: utf-8 -*-
import math
import re
import numpy as np
from operator import itemgetter
import jieba
import jieba.posseg as pseg;list(pseg.dt.cut("123,456"))
from collections import defaultdict
from read_config import stopwords_path
from analysis_package.extract_phrase import ExtractPhrase
from fta.common_class import do_commom_class

# 获取停用词
def get_stopwords():
    filter_set = set()
    with open(stopwords_path, "r",encoding="utf-8") as f:
        str_data = f.read()
    for d in str_data.split("\n"):
        s = d.strip()
        filter_set.add(s)
        if len(s)>0:
            filter_set.add(s[0].upper()+s[1:])
    return filter_set
#filter_set = get_stopwords()

# 无向图，用于存储图数据以及计算textrank
class UndirectWeightGraph(object):

    def __init__(self, min_weight=0.05):
        self.graph = defaultdict(dict)
        self.d = 0.85
        self.max_iter = 5
        self.min_weight = min_weight
        self.edge_count = 0
        self.node_set = set([])
        self.edge_list = []

    def add_edge(self, p1, p2, weight, X=None):
        if X==None:
            X=[10000,10]
        if weight < self.min_weight:
            return
        self.graph[p1][p2] = weight
        self.graph[p2][p1] = weight
        #随着添加的边数的增加，不断提高权重的上限。
        self.edge_count += 1
        self.min_weight += (weight-self.min_weight) / (X[0] + X[1]*self.edge_count)

    def get_graph_count(self):
        node_count=0
        edge_count=0
        for k,v in self.graph.items():
            node_count+=1
            edge_count += len(v)
        return node_count, edge_count/2

    def rank(self):
        gamma = [0.4, 0.4, 0.3, 0.2, 0.1, 0, 0, 0, 0, 0,]
        ws = defaultdict(float)
        out_sum = defaultdict(float)

        wsd = 1.0 / (len(self.graph) or 1.0)

        for k, v in self.graph.items():
            out_sum[k] = sum([val for val in v.values()])
            ws[k] = wsd

        for i in range(self.max_iter):

            ws_tmp = defaultdict(float)
            sum_new_val = 0
            num_node = 0
            for k in [k for k in self.graph.keys()]:
                v = self.graph[k]
                s = 0
                for p,w in v.items():
                    s += w * ws[p] / out_sum[p]
                new_val = (1-self.d) + self.d * s
                sum_new_val += new_val
                num_node += 1
                ws_tmp[k] = new_val

            #每一轮迭代都淘汰掉一部分数量的候选节点
            #当无向图中的节点数足够少（100以内）时就无需再通过节点淘汰进行加速了。
            if gamma[i] > 0.0001 and num_node > 100:
                min_val = sum_new_val*gamma[i] / (0.1+num_node)
                for p,val in [(p,val) for p,val in ws_tmp.items()]:
                    if val < min_val:
                        for k in [k for k in self.graph[p].keys()]:
                            del self.graph[k][p]
                        del self.graph[p]
                ws = ws_tmp
        return ws

control_chars = ''.join(map(chr, [i for i in range(0,32)] + [i for i in range(127,160)]))
control_char_re = re.compile('[%s]' % re.escape(control_chars))

def _rank(edge_dict=None, top_num=10, node_num=100):
    if edge_dict==None:
        edge_dict={}
    g = UndirectWeightGraph()
    #根据财富分配的二八定律，只有前20%的权重较大的边是重要的。
    #80%权重较小的边对于textrank算法的贡献度可以忽略，
    #如此就能极大减少无向图的边数，将textrank算法性能提高5倍。
    #详见:https://baijiahao.baidu.com/s?id=1614852492116561892&wfr=spider&for=pc
    weight_list = sorted([wo for wo in edge_dict.values()])
    len_weight_list = len(weight_list)
    if len_weight_list < 10000:
        min_weight = 0
    else:
        pos = max(int(0.8 * len_weight_list), 10000)
        min_weight = weight_list[pos-1]
    for key, value in edge_dict.items():
        if value > min_weight:
            g.add_edge(key[0], key[1], value)

    words_ww = g.rank()
    for i in range(min(top_num,node_num)):
        if i not in words_ww:
            words_ww[i] = -i
    tags = sorted(words_ww.items(), key=itemgetter(1), reverse=True)
    # tags2 = sorted(words_ww, key=words_ww.__getitem__, reverse=True)
    return tags

stopwords = get_stopwords()
def extract_words(cont):
    sentences = cont.strip()
    sentence_w=[]
    if len(sentences)>0:
        for wo,flag in pseg.dt.cut(sentences):
            if wo not in stopwords :
                sentence_w.append((wo,flag))
        return sentences,sentence_w

def content2wordlist(str_content):  
    str_content = control_char_re.sub(' ',str_content)
    contents = re.split("[。！，？.!?,\n\t(\r\n)]", str_content)
    wordlist=[]
    sentence_list=[]
    result_list = [extract_words(cont) for cont in contents]
    for i in result_list:
        if i !=None:
            wordlist.append(i[1])
            sentence_list.append(i[0])
    cut_result={}
    cut_result['wordlist']=wordlist
    cut_result['sentences']=sentence_list
    return cut_result

def wordlist2keywords(wordlist, key_num=10, big_k=5, allow_pos=('nr', 'ns', 'nz', 'nt', 'nrt', 'n', 'v', 'l','eng')):  
    #获取文本下的关键词
    # wordlist=content2wordlist(str_content)['wordlist']
    candicate_words = dict()
    words_pair = defaultdict(int)
    candicate_words_list = []
    sentence_phrase_list = []

    def get_index(tword):
        if tword not in candicate_words:
            candicate_words[tword] = len(candicate_words)
            candicate_words_list.append(tword)
        return candicate_words[tword]
    for sentencs_word in wordlist:
        sentences_words = []
        sentence_used_by_phrase = []     
        for wo, flag in sentencs_word:
            sentence_used_by_phrase.append(wo)
            if len(wo) > 1 and flag in allow_pos:
                sentences_words.append(wo)

        sentence_phrase_list.append(sentence_used_by_phrase)
        if len(sentences_words):
            for k, word in enumerate(sentences_words):
                wd_id = get_index(word)
                for nwd in sentences_words[k+1:k + big_k]:
                    nwd_id = get_index(nwd)
                    words_pair[(wd_id, nwd_id)] += 1
                for nwd in sentences_words[max(0, k-big_k):k]:
                    nwd_id = get_index(nwd)
                    words_pair[(wd_id, nwd_id)] += 1
    words_ww = _rank(words_pair, key_num, len(candicate_words_list))
    keywords = [(candicate_words_list[wo[0]],wo[1] )for wo in words_ww]  
    return keywords,sentence_phrase_list
#关键词到关键短语
def keyword2keyphrase(sentence_phrase_list, keywords):
    ep = ExtractPhrase(sentence_phrase_list, keywords)
    ep.statistics_tf_info()
    n_gram_list = ep.cacl_lr_entropy()
    for i in range(len(keywords)):
        kw = keywords[i]
        for n_gram in n_gram_list[:len(keywords)]:
            if kw in n_gram:
                keywords[i] = ''.join(n_gram).strip()
                n_gram_list.remove(n_gram)
                break
    return keywords

#摘要
def wordlist2abstract(cut_result):
    wordlist = cut_result['wordlist']
    sentence_list= cut_result['sentences']
    sentences_list = []
    #sentences_dict = {}
    orient_sentences_list =[]
    # jd = JiebaDict()
    # for sen_word in wordlist:
    for i in range(len(wordlist)):   
        sentences_words = []
        sentences_words_len = 0
        sentences_words_set = set()
        for w,flag in wordlist[i]:
            w = w.strip()
            # if w in jd.word_dict:
                # sentences_words_set.add(jd.word_dict[w][1])
            sentences_words_set.add(w)
            sentences_words_len += 1
            if len(w)>1 :
                sentences_words.append(w)
            
        if sentences_words_len > 2:
            # orient_sentences_list.append("".join(i[0] for i in sen_word))
            orient_sentences_list.append(sentence_list[i])
            sentences_list.append((sentences_words_len,sentences_words_set))

    sentences_len = len(orient_sentences_list)
    #X = [1000000/(1e-5+sentences_len), 100000/(1e-5+sentences_len)]
    edge_dict = {}
    for i in range(sentences_len -1):
        i_sentences_len,i_sentences_set = sentences_list[i]
        #随着文章的深入动态调整窗口大小,窗口最大达到500后缓慢减小。
        window_size = min(1000, int(100 + 10000/(1+i)))
        top_j = min(i + window_size, sentences_len)
        for j in range(i + 1, top_j):
            j_sentences_len,j_sentences_set = sentences_list[j]
            #此处速度较慢，需优化
            w = len(i_sentences_set & j_sentences_set) / math.log1p(i_sentences_len*j_sentences_len)
            edge_dict[(i,j)] = w
    sentence_weight = _rank(edge_dict,10,len(orient_sentences_list))
    sentences=[i[0] for i in sentence_weight]
    abstract_result = "。".join(map(lambda y: y[1], sorted([(i, orient_sentences_list[i]) for i in sentences[:5]], key=lambda x: x[0])))
    return abstract_result

#指纹
def keywords2fingerprint(keyword):
    #print("content_length:%s"%(len(content)))
    #keyword = jieba.analyse.extract_tags(content, topK=30, withWeight=True, allowPOS=('n', 'nr','nt','ns','v','vn'))
    # keyword = self.keywords(content)
    hash_list =[]
    if len(keyword)==0:
        return "" 
    for word,weight in keyword:
        # weight = int(weight*10)
        weight = weight*10
        word_hash = word_to_hash(word)
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
def word_to_hash(word):
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

def wordlist2commonclass(wordlist):
    result= do_commom_class(wordlist)     
    return result



