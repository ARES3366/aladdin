import time
import math,random
from collections import defaultdict
#from collections import Counter

class ExtractPhrase():
    #@sentence_list: 文本短句分词后结果。格式如：
    # [
    #    ["因为", "我"，"是"，"一个"，"中国人"],
    #    ["所以","我","爱","中国"]
    # ]
    def __init__(self, sentence_list, keywords):
        self.sentence_list = sentence_list
        self.keywords = keywords
        self.tf_info = {1:defaultdict(float), 2:defaultdict(float), 3:defaultdict(float)}
        self.mutual_info = defaultdict(float)
        #多元词左边出现的所有可能、如果左边没有词用随机字符串替代
        self.left_word_info = defaultdict(dict)
        #多元词右边出现的所有可能、如果右边没有词用随机字符串替代
        self.right_word_info = defaultdict(dict)
        #多元词的左熵
        self.left_entropy_info = defaultdict(float)
        #多元词的右熵
        self.right_entropy_info = defaultdict(float)

    #统计一元词、二元词、三元词的词频
    def statistics_tf_info(self):
        #tf = defaultdict(int)
        N = 0
        for sentence in self.sentence_list:
            len_sentence = len(sentence)
            N += len_sentence
            last_appear_key = 10
            for i in range(len_sentence):
                w = sentence[i]
                last_appear_key = 0 if w in self.keywords else last_appear_key+1
                self.tf_info[1][w] += 1 #一元词出现的次数
                if i>0 and last_appear_key<2:
                    w = (sentence[i-1], sentence[i])
                    self.tf_info[2][w] += 1 #二元词出现的次数
                    left_w = random.random() if i == 1 else sentence[i-2]
                    if left_w not in self.left_word_info[w]: self.left_word_info[w][left_w] = 0
                    self.left_word_info[w][left_w] += 1
                    right_w = random.random() if i==len_sentence-1 else sentence[i+1]
                    if right_w not in self.right_word_info[w]: self.right_word_info[w][right_w] = 0
                    self.right_word_info[w][right_w] += 1
                if i>1 and last_appear_key<3:
                    w = (sentence[i-2],sentence[i-1],sentence[i])
                    self.tf_info[3][w] += 1 #三元词出现的次数
                    left_w = random.random() if i == 2 else sentence[i-3]
                    if left_w not in self.left_word_info[w]: self.left_word_info[w][left_w] = 0
                    self.left_word_info[w][left_w] += 1
                    right_w = random.random() if i==len_sentence-1 else sentence[i+1]
                    if right_w not in self.right_word_info[w]: self.right_word_info[w][right_w] = 0
                    self.right_word_info[w][right_w] += 1

        for w in self.tf_info[1]:
            self.tf_info[1][w] /= N
        for w in self.tf_info[2]:
            self.tf_info[2][w] /= N
        for w in self.tf_info[3]:
            self.tf_info[3][w] /= N
         
    def cacl_mutual_info(self):
        #计算二元词的互信息
        for w,tf in self.tf_info[2].items():
            self.mutual_info[w] = math.log(float(tf) / (self.tf_info[1][w[0]]*self.tf_info[1][w[1]]))
        #计算三元词的互信息
        for w,tf in self.tf_info[3].items():
            self.mutual_info[w] = math.log(float(tf) / (self.tf_info[1][w[0]]*self.tf_info[1][w[1]]*self.tf_info[1][w[2]]))

    #计算多元词的左右熵
    #左右熵: 分为左熵与右熵，表示n元词左边或右边出现的词的词频分布的熵。
    #            0表示只出现了一次或者出现多次时左边或右边的词总是同一个词。
    #            >0表示在语料中出现了多次，而且每次出现时左边或右边的不总是相同的
    #@threshold:  左右熵的阈值高于此阈值时n元词才可能被认为是一个短语
    def cacl_lr_entropy(self, threshold=1):
        ret_n_gram_list = []
        for w, count_info in self.left_word_info.items():
            N = sum(count_info.values())
            el = 0
            for _,num in count_info.items():
                p = float(num)/N
                el -= p*math.log(p)

            count_info = self.right_word_info[w]
            N = sum(count_info.values())
            er = 0
            for _,num in count_info.items():
                p = float(num)/N
                er -= p*math.log(p)

            if el > threshold:
                self.left_entropy_info[w] = el
            if er > threshold:
                self.right_entropy_info[w] = er
            if el > threshold and er > threshold:
                ret_n_gram_list.append((w, el+er))

        ret_n_gram_list.sort(key=lambda x : x[1], reverse=True)
        return [x[0] for x in ret_n_gram_list]

if __name__ == '__main__':
    sentence_list=[
      ['牛顿', '是', '英国', '著名', '科学家'],
      ['爱因斯坦', '是', '德国', '著名', '科学家'],
      ['钱学森', '是', '中国', '著名', '科学家'],
      ['C罗', '是', '葡萄牙', '著名', '足球', '运动员'],
      ['梅西', '是', '阿根廷', '著名', '足球', '运动员'],
      ['德罗巴', '是', '法国', '著名', '足球', '运动员'],
      ['支持', '向量', '机', '过去', '被', '经常', '用于', '做', '二分类'],
      ['支持', '向量', '机', '现在', '却', '很少', '再', '被', '使用'],
      ['支持', '向量', '机', '可能', '已经', '过时', '了'],
    ]
    sentence_list *= 1000
    keywords = ['是', '牛顿', '著名', '科学家', '足球', '支持', '向量']
    t0=time.time()
    ep = ExtractPhrase(sentence_list, keywords)
    t1=time.time()
    ep.statistics_tf_info()
    t2=time.time()
    #ep.cacl_mutual_info()
    n_gram_list = ep.cacl_lr_entropy()
    t3=time.time()
    #print(ep.tf_info)
    #print(ep.mutual_info) 
    print(ep.left_entropy_info) 
    print(ep.right_entropy_info) 
    print(n_gram_list)
    print(t1-t0, t2-t1, t3-t2)
