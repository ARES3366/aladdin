#import logging
import math
import re
import jieba
import jieba.posseg as pseg
import jieba.analyse
from collections import defaultdict
from read_config import stopwords_path
from acam_dict import WordTree
from utils import singleton
from zhtools.langconv import Converter
from .extract_phrase import ExtractPhrase

# 获取停用词
def get_stopwords():

    # filter_set = set(["\n", "\r", "，", "。", "“", "”", "(", "", "！", "：", "？", "、", "《", "》",
    # "\"", "!", "…", "?",
    #                   "-", "；", "Ｉ", "Ｈ", "＝", "Ｖ", ".", "‘", "’"])
    # hanzi_fset = set(["的", "了", "在", "是", "他", "我", "你", "和", "０", "人", "也", "她", "有",
    # "不", "就", "又", "一",
    #                   "一个", "他们", "年", "我们", "说", "吧", "对", "中", "上", "都", "它", "到", "之",
    # "着", "道", "知道",
    #                   "时候", "不到", "没有", "不能", "才能"])
    # shuzi_fset = set(["１", "９", "２", "５", "３", "1"])
    # filter_set = filter_set | hanzi_fset | shuzi_fset
    # return filter_set
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

@singleton
class JiebaDict():
    def __init__(self):
        self.word_dict = {}
        self.word_list = []
        with jieba.get_dict_file() as fp:
            wid = 0
            for line in fp:
                w, _, flag = line.decode('utf8').split()
                w_cht = Converter('zh-hant').convert(w)
                self.word_dict[w] = (flag,wid)
                self.word_dict[w_cht] = (flag,wid)
                wid += 1
                if len(w) > 1:
                    self.word_list.append(w)
                    self.word_list.append(w_cht)
        self.acam = self.create_acam()

    def create_acam(self):
        wt = WordTree({'#','@','$'})
        wt.build(self.word_list)
        return wt

    def fast_cut(self, text):
        return self.acam.search_cut(text)

control_chars = ''.join(map(chr, [i for i in range(0,32)] + [i for i in range(127,160)]))
control_char_re = re.compile('[%s]' % re.escape(control_chars))
# 提取关键词
def extract_keywords(str_content, key_num=10, allow_pos=('nr', 'ns', 'nz', 'nt', 'nrt', 'n', 'v', 'l','eng'), level=2, big_k=5, extract_phrase=True):
    """
    :param str_content:
    :param key_num:
    :param allow_pos tuple 候选词性
    :return: list<str>()
    """
    str_content = control_char_re.sub(' ',str_content)
    candicate_words = dict()
    contents = re.split("[。！，？.!?,\n\t(\r\n)]", str_content)
    words_pair = defaultdict(int)
    candicate_words_list = []
    sentence_phrase_list = []
    #global filter_set
    filter_set = get_stopwords()
    jd = JiebaDict()

    def get_index(tword):
        if tword not in candicate_words:
            candicate_words[tword] = len(candicate_words)
            candicate_words_list.append(tword)
        return candicate_words[tword]
    for cont in contents:
        sentences = cont.strip()
        sentences_words = []
        sentence_used_by_phrase = []
        if level in [0,1,2]:
            if level == 0:
                gen = jd.fast_cut(sentences)
            elif level == 1:
                gen = jieba.cut(sentences,cut_all=True)
            elif level == 2:
                gen = jieba.cut(sentences,cut_all=False)
            for w in gen:
                w = w.strip()
                if w not in filter_set:
                    sentence_used_by_phrase.append(w)
                    if len(w) > 1 and w in jd.word_dict and jd.word_dict[w][0] in allow_pos:
                        sentences_words.append(w)

        elif level == 3:
            for w, flag in pseg.dt.cut(sentences):
                if w not in filter_set:
                    sentence_used_by_phrase.append(w)
                    if flag in allow_pos and len(w) > 1:
                        sentences_words.append(w)

        sentence_phrase_list.append(sentence_used_by_phrase)
        if level in [0,1,2,3]:
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
    keywords = [candicate_words_list[w] for w in words_ww[:key_num]]
    if not extract_phrase: return keywords
    ep = ExtractPhrase(sentence_phrase_list, keywords)
    ep.statistics_tf_info()
    n_gram_list = ep.cacl_lr_entropy()
    for i in range(len(keywords)):
        kw = keywords[i]
        for n_gram in n_gram_list[:key_num]:
            if kw in n_gram:
                keywords[i] = ''.join(n_gram).strip()
                n_gram_list.remove(n_gram)
                break
    return keywords

def _rank(edge_dict=None, top_num=10, node_num=100):
    if edge_dict==None:
        edge_dict={}
    g = UndirectWeightGraph()
    #根据财富分配的二八定律，只有前20%的权重较大的边是重要的。
    #80%权重较小的边对于textrank算法的贡献度可以忽略，
    #如此就能极大减少无向图的边数，将textrank算法性能提高5倍。
    #详见:https://baijiahao.baidu.com/s?id=1614852492116561892&wfr=spider&for=pc
    weight_list = sorted([w for w in edge_dict.values()])
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
       
    return sorted(words_ww, key=words_ww.__getitem__, reverse=True)

# 提取关键词 jieba 实现
def extract_keywords_jieba(str_content, key_num=10, allow_pos=('ns', 'n', 'v')):
    """
    :param str_content: str
    :param key_num: int
    :param allow_pos tuple 候选词性
    :return:
    """
    keywords = jieba.analyse.textrank(str_content, topK=key_num, withWeight=False, allowPOS=allow_pos)
    return keywords

# 提取摘要
#def extract_abstract(str_content, sim_score=0.05):
def extract_abstract(str_content):
    """
    :param str_content: str
    :param sim_score float 句子相似度阈值
    :return: str
    """
    sentences_list = []
    #sentences_dict = {}
    orient_sentences_list = []
    #global filter_set
    filter_set = get_stopwords()
    contents = re.split("[。！？.!?\n\t(\r\n)]", str_content)
    jd = JiebaDict()
    for cont in contents:
        sentences = cont.strip()
        sentences_words = list(jieba.cut(sentences))
        #sentences_words = list(jd.fast_cut(sentences))
        sentences_words_len = 0
        sentences_words_set = set()
        for word in [word.strip() for word in sentences_words]:
            if word not in filter_set and word in jd.word_dict:
                sentences_words_set.add(jd.word_dict[word][1])
                sentences_words_len += 1
            
        if sentences_words_len > 2:
            orient_sentences_list.append(sentences)
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

    sentence_weight = _rank(edge_dict, 10, len(orient_sentences_list))
    abstract_result = " ".join(map(lambda y: y[1], sorted([(i, orient_sentences_list[i])
                                                           for i in sentence_weight[:5]], key=lambda x: x[0])))
    return abstract_result

#对两个接口进行合并，关键词与摘要一起提取，只做一次分词。
def extract_keywords_abstract(str_content, key_num=10,allow_pos=('nr', 'ns', 'nz', 'nt', 'nrt', 'n', 'v'), big_k=5):
    candicate_words = dict()
    contents = re.split("[。！？.!?\n\t(\r\n)]", str_content)
    words_pair = defaultdict(int)
    candicate_words_list = []
    
    sentences_list = []
    #sentences_dict = {}
    orient_sentences_list = []

    #global filter_set
    filter_set = get_stopwords()
    jd = JiebaDict()
    
    def get_index(tword):
        if tword not in candicate_words:
            candicate_words[tword] = len(candicate_words)
            candicate_words_list.append(tword)
        return candicate_words[tword]

    for cont in contents:
        sentences = cont.strip()
        sentences_words = []
        sentences_words_len = 0
        sentences_words_set = set()

        gen = jieba.cut(sentences, cut_all=False)
        for w in gen:
            w = w.strip()
            if w not in filter_set and w in jd.word_dict:
                sentences_words_set.add(jd.word_dict[w][1])
                sentences_words_len += 1
                if len(w)>1 and jd.word_dict[w][0] in allow_pos:
                    sentences_words.append(w)

        if len(sentences_words):
            for k, word in enumerate(sentences_words):
                wd_id = get_index(word)
                for nwd in sentences_words[k+1:k + big_k]:
                    nwd_id = get_index(nwd)
                    words_pair[(wd_id, nwd_id)] += 1
                for nwd in sentences_words[max(0, k-big_k):k]:
                    nwd_id = get_index(nwd)
                    words_pair[(wd_id, nwd_id)] += 1
            
        if sentences_words_len > 2:
            orient_sentences_list.append(sentences)
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

    words_ww = _rank(words_pair, key_num, len(candicate_words_list))
    keywords = [candicate_words_list[w] for w in words_ww[:key_num]]
    sentence_weight = _rank(edge_dict,10,len(orient_sentences_list))
    abstract_result = " ".join(map(lambda y: y[1], sorted([(i, orient_sentences_list[i])
                                                           for i in sentence_weight[:5]], key=lambda x: x[0])))
    return keywords, abstract_result

