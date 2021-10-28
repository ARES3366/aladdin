# -*- coding:utf-8 -*-
import numpy as np
class DocFingerprintCluster:
    #传入参数，初始化
    def __init__(self,fingerprintdbs,grad=3):
        self.fingerprintdbs = fingerprintdbs
        self.grad = grad
        self.index_result = []
        self.doc_names_list = []
        self.fingerprints_list = []
        self.cluster_result = []
        self.__init_others()
        self.hm_dis_matrix = self.__gen_hm_dis_matrix(len(self.doc_names_list))
    #初始化文件名列表和相对应得指纹数据列表
    def __init_others(self):
        fingerprintdb = {}
        for key, val in self.fingerprintdbs.items():
            if val == "":
                #fingerprint_is0 = []
                #fingerprint_is0.append(key)
                #self.cluster_result.append(fingerprint_is0)
                fingerprintdb[key] = 0
            else:
                fingerprintdb[key] = int(val)
        self.doc_names_list = list(fingerprintdb.keys())
        self.fingerprints_list = list(fingerprintdb.values())

    #生成海明距离矩阵
    def __gen_hm_dis_matrix(self, sum_text):
        hm_dis_matrix = np.zeros((sum_text, sum_text))
        for i in range(sum_text):
            if self.fingerprints_list[i]==0:
                for j in range(sum_text):
                    if j==i:
                        hm_dis_matrix[i][j] =0
                    else:
                        hm_dis_matrix[i][j] = 64
            else:
                for j in range(sum_text):
                    if self.fingerprints_list[j]==0:
                        hm_dis_matrix[i][j] =64
                    else:
                        hm_dis_matrix[i][j] = bin(self.fingerprints_list[i] ^ self.fingerprints_list[j]).count("1")
        return hm_dis_matrix.astype(np.int8)
    #索引聚类数据整合成文件名聚类数据
    def __index2name(self):
        # result为索引聚类结果，其中的数据为文本的索引数据，与doc_names_list进行整合，转成文件名的聚类结果
        for idx_set in self.index_result:
            file_name_list = []
            for idx in idx_set:
                file_name_list.append(self.doc_names_list[idx])
            self.cluster_result.append(file_name_list)
        return self.cluster_result
    #聚类
    def __cluster(self):
        #海明距离矩阵
        H = self.hm_dis_matrix
        #文本数量
        N = len(self.doc_names_list)
        #按列排序后得每列第二个数据
        I = np.sort(H,axis=0)[1,:]
        alread_cluster_idx_set = set([])
        for i in range(N):
            if i in alread_cluster_idx_set: continue
            idx_list_must=[i]
            idx_list_may=[]
            for j in range(i + 1, N):
                if H[i, j] <= self.grad and j not in alread_cluster_idx_set:
                    if H[i, j] == I[j]:
                        idx_list_must.append(j)
                    else:
                        idx_list_may.append(j)
            idx_list=idx_list_must.copy()
            for j in idx_list_may:
                min_dist = min([H[j,i] for i in idx_list_must])
                if min_dist == I[j]: idx_list.append(j)
            alread_cluster_idx_set.update(idx_list)
            self.index_result.append(idx_list)

    def cluster(self):
        #聚类
        self.__cluster()
        #返回文件名得聚类结果
        return self.__index2name()


