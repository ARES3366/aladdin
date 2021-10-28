# coding=utf-8

import numpy as np
import os
from collections import Counter
# from pyhanlp import HanLP
# from textrank4zh import TextRank4Keyword
import math
from collections import defaultdict
import pymysql
import re
from read_config import stopwords_path
import jieba
import jieba.analyse
# import asyncio
from auto_text_filter.operate_atf_db import insert_words_2_mysql
from multiprocessing import Queue,Pool,cpu_count
# jieba.analyse.extract_tags('',topK=1,allowPOS=('n','nr','ns', 'nz', 'nt', 'nrt',  'v', 'vn','l','eng'))
jieba.analyse.extract_tags('',topK=1)

# 定义删除除字母,数字，汉字以外的所有符号的函数
# def remove_punctuation(line):
#     line = str(line)
#     if line.strip() == '':
#         return ''
#     rule = re.compile(u"[^a-zA-Z\u4E00-\u9FA5]")
#     line = rule.sub('', line)
#     return line

# 停用词
# 获取停用词
def get_stopwords():
    stopwords_set = set()
    with open(stopwords_path, "r", encoding="utf-8") as f:
        str_data = f.read()
    for d in str_data.split("\n"):
        s = d.strip()
        stopwords_set.add(s)
        if len(s) > 0:
            stopwords_set.add(s[0].upper() + s[1:])
    return stopwords_set

stopwords = get_stopwords()
def extract_(args):
    con_name = args[0]
    content = args[1]
    content = content.replace('.','')
    content = content.replace('_','')
    cutone = jieba.analyse.extract_tags(content[:10000], topK=100)
    if len(cutone)<=2:return None,None
    i=0
    words=''
    for word in cutone:
        if word not in stopwords and not word.isdigit():
            words += word + ' '
            i+=1
    if i>2:
        return con_name,words.strip()
    else:
        return None,None

# 传入得参数是json格式content_data，key是文件名，val是文件内容
def get_keywords_data(content_dict):
    # stopwords = get_stopwords()
    file_keywords = {}
    # N = cpu_count()
    N = min(cpu_count(),8)
    #利用多进程，提高分词的效率
    with Pool(N) as pool:
        result_list = pool.map(extract_, [(con_name, content_['content']) for con_name, content_ in content_dict.items()])
        for i in result_list:
            if i[0] !=None:
                file_keywords[i[0]]=i[1]
        return file_keywords

    # import time
    # t1=time.time()
    # for con_name, content_ in content_data.items():
    #     content = content_['content']
    #     content = remove_punctuation(content)
    #     cutone = jieba.analyse.extract_tags(content, 100)
    #     words = ''
    #     for word in cutone:
    #         if word not in stopwords:
    #             words += word + ' '
    #     file_keywords[con_name] = words
    # t2=time.time()
    # print("提取关键短语用时：",(t2-t1))
    # return file_keywords

# word转成加密后得16进制字符串
# def word2hash(w):
#     o=hashlib.md5(w.encode('utf8'))
#     value = o.hexdigest()
#     return int(value[:8], 16)

def get_tfidf_dict(file_keywords):
    file_name = []
    documents = []
    for f_name, doc in file_keywords.items():
        file_name.append(f_name)
        documents.append(doc)
    df = defaultdict(int)
    counter_list = []
    N = 0
    for doc in documents:
        N += 1
        word_list = doc.split()
        counter_list.append(Counter(word_list))
        for w in set(word_list):
            df[w] += 1
    word_list = []
    idf = []
    for k, v in df.items():
        word_list.append(k)
        idf.append(v)
    idf = np.array(idf).astype(np.float)
    idf += 1
    idf = idf / (N + 1)
    idf = 1 - np.log(idf)
    word_dict = {w: idx for idx, w in enumerate(word_list)}
    results = []
    for counter in counter_list:
        tfidf = {}
        s = 0
        for w, f in counter.items():
            wid = word_dict[w]
            v = f * idf[wid]
            tfidf[w] = v
            s += v ** 2
        s = s ** 0.5
        for w in tfidf:
            tfidf[w] /= s
        results.append(tfidf)
    # print(results)
    return file_name, results, N

def get_similar_matrix(tfidf_v, N):
    S = np.zeros([N, N])
    for i in range(N - 1):
        for j in range(i + 1, N):
            a = tfidf_v[i]
            b = tfidf_v[j]
            v = 0
            for w in a:
                if w in b:
                    v += a[w] * b[w]
            S[i, j] = v
    S += S.T
    for i in range(N): S[i, i] = 1
    # print(S)
    return S
# 利用相似度矩阵进行聚类
def cluster(similar, n_clusters, alg='ncut'):
    W = similar
    N = len(similar)

    # N = W.shape[0]
    # 生成W矩阵
    def dealW(W=W):
        _W = np.argsort(-W, axis=1)
        sigma = int(N / n_clusters)
        distance = np.zeros(W.shape)
        distance[np.arange(N)[:, np.newaxis], _W] = np.arange(N)[np.newaxis, :]
        W = np.exp(-0.5 * (distance / sigma) ** 2)
        W += W.T
        W /= 2
        return W
    W = dealW()
    # 生成D矩阵
    D = np.diag(np.sum(W, axis=1))
    A = np.diag(np.sum(W, axis=1) ** (-0.5))
    # 生成拉普拉斯矩阵
    # if alg == 'nCut':
    L = np.matmul(np.matmul(A, D - W), A)
    # elif alg == 'minCut':
    #     L = D - W
    # 计算特征值和特征向量
    eigval, vec = np.linalg.eig(L)
    eigval, vec = eigval.real, vec.real
    idx = eigval.argsort()
    sorted_eigval = eigval[idx]
    # if alg == 'nCut':
    for i in range(len(sorted_eigval)):
        if sorted_eigval[i] > (1 - 1 / n_clusters) * 0.95:
            break
    # elif alg == 'minCut':
    #     i = n_clusters
    data = vec[np.arange(N)[:, np.newaxis], idx[np.newaxis, :n_clusters]]
    data /= ((np.sum(data ** 2, axis=0)) ** 0.5)[np.newaxis, :]
    if alg == 'nCut': data = np.matmul(A, data)
    data = np.matmul(data, np.diag(-np.log(sorted_eigval[:n_clusters] + 1e-10)))
    # print(sorted_eigval[:i])
    from sklearn.cluster import KMeans
    kmeans_model = KMeans(n_clusters=n_clusters).fit(data)
    return kmeans_model.labels_, i, sorted_eigval[:i]

def get_cluster_name_keywords(file_content, cluster_num=1):
    status_result={'status':0}
    # file_content = read_data_from_local(file_content)
    file_keywords = get_keywords_data(file_content)
    if len(file_keywords)< cluster_num: 
        status_result={'status':1,'message':'The number of text that can be clustered is less than the number of clusters'}
        return {},{},{},status_result
    # print(file_keywords)
    file_name, tfidf_dict, N = get_tfidf_dict(file_keywords)
    similar = get_similar_matrix(tfidf_dict, N)
    # print(file_name)
    n_cluster_list = []
    rate_list = []
    if cluster_num <= 1:
        # 选取一个聚类效果比较好得聚类个数进行聚类
        for n_clusters in range(2, 10):
            if n_clusters>=len(similar):
                break
            labels, i, eigval = cluster(similar, n_clusters=n_clusters, alg='nCut')
            hist, bins = np.histogram(labels, n_clusters)

            rate = hist.min() / hist.max()
            if n_clusters <= i:
                n_cluster_list.append(n_clusters)
                rate_list.append(rate)
        cluster_num = n_cluster_list[rate_list.index(max(rate_list))]
    C, i, eigval = cluster(similar, n_clusters=cluster_num, alg='nCut')
    # 整合聚类结果，把索引换成名字，及对应得类关键词
    # C = kmeans_model.labels_
    # print(C)
    cluster_index = defaultdict(list)
    cluste_keywords = defaultdict(list)
    cluster_name = defaultdict(list)
    for i in range(len(C)):
        cluster_name[C[i]].append(file_name[i])
        cluster_index[C[i]].append(i)
        # cluste_keywords[C[i]].append(file_keywords[file_name[i]].split(' '))
        cluste_keywords[C[i]].append(file_keywords[file_name[i]])

    # print(cluste_keywords)
    # 计算出同类文档中的平均相似度
    cluster_min_sim = {}
    for c, indexs in cluster_index.items():
        sims = similar.take(indexs, axis=1).take(indexs, axis=0)
        ave_sim = np.average(sims)
        cluster_min_sim[c] = ave_sim
    return cluster_name, cluste_keywords, cluster_min_sim , status_result

# 查找一个类别名，此类别下出现次数最高的关键词
def find_class_name(cluste_words):
    class_name=[]
    for key,val in cluste_words.items():
        words=[]
        for i in val:
            words.extend(i.split(' '))
        res = Counter(words)
        d = sorted(res.items(), key=lambda x: x[1], reverse=True)
        name = d[0][0]+'_'+d[1][0]
        class_name.append(name)
    return class_name

# 执行聚类
def spectral_cluster(file_content, taskid, cluster_num=1):
    
    cluste_index, cluste_words, cluster_aver_sim,status_result = get_cluster_name_keywords(file_content,cluster_num=cluster_num)
    if status_result['status']==1:return status_result
    cluster_result = {}
    # 把聚类完成后的的类别名改成类别下的关键词的前两个组成的新类别名，默认类别名，用户可修改
    new_class_name_list = find_class_name(cluste_words)

    # for key, val in wordtfidf.items():
    #     new_class_name = val[0]
    #     new_class_name_list.append(new_class_name)
    cluste_name_values = cluste_index.values()
    # cluste_words_values = cluste_words.values()
    cluste_avr_simi_values = cluster_aver_sim.values()
    # cluster_keywords_values = wordtfidf.values()
    cluster_name_result = dict(zip(new_class_name_list, cluste_name_values))
    # cluster_words_result = dict(zip(new_class_name_list, cluste_words_values))
    cluster_aver_sim_reslut = dict(zip(new_class_name_list, cluste_avr_simi_values))
    # cluster_keywords_result = dict(zip(new_class_name_list, cluster_keywords_values))

    keywords_file={}
    for key,files in cluste_index.items():
        for i in range(len(files)):
            keywords_file[files[i]]=cluste_words[key][i]
    # for key,val in cluster_keywords_result.items():
    #     for w in val:
    #         for i in range(len(cluster_words_result[key])):
    #             if w in cluster_words_result[key][i]:
    #                 keywords_file.append((w,cluster_name_result[key][i]))

    cluster_result['cluste_name'] = cluster_name_result
    cluster_result['file_words'] = keywords_file
    # cluster_result['cluste_keywords'] = cluster_keywords_result
    cluster_result['cluste_ave_simi'] = cluster_aver_sim_reslut
    cluster_result['taskid'] = taskid
    # print(cluster_result)
    # 聚类结果，类别及关键词存入到数据库
    # result_insert_taskid = await insert_taskid(taskid)
    # if result_insert_taskid['status'] == 1: return result_insert_taskid
    result = insert_words_2_mysql(cluster_result)
    if result['status'] == 1: return result
    return {'status': 0, 'taskid':taskid,'message': '聚类完成，条件已插入数据库'}
    # return cluster_result


