# -*- conding:utf-8 -*-
import jieba
from analysis_package.ac_search import Trie
import os
import re
from collections import defaultdict
 
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__), path))


stoptext=open(_get_module_path('../conf/stopwords.txt'),encoding='utf-8')
stopwords=[' ',]
for word in stoptext:
    word = word.strip()
    stopwords.append(word)

def tf_sort(wordlist):
    count_dict = defaultdict(lambda: 0)
    for item in wordlist:
        count_dict[item] +=1
    return sorted(count_dict.items(),key=lambda x:x[1],reverse=True)
# 定义删除除字母,数字，汉字以外的所有符号的函数
def remove_punctuation(line):
    line = str(line)
    if line.strip() == '':
        return ''
    rule = re.compile(u"[^a-zA-Z\u4E00-\u9FA5]")
    line = rule.sub('', line)
    return line

def get_abstract_from_text_interception(content):
    content=remove_punctuation(content)
    keyword2weight={}
    words=[]
    seg = [w for w in jieba.cut(content, cut_all=True)]
    count_result = tf_sort(seg)
    for i, j in count_result:
        if len(i) < 2 or i in stopwords:
            continue
        else:
            keyword2weight[i] = j
            words.append(i)
        if len(keyword2weight) >= 15:
            break

    model = Trie(words)
    a = model.search(content)
    b={}
    for k,v in a.items():
        for p in v:
            b[p[0]]=k
    d=sorted(b.items(),key=lambda x:x[0],reverse=False)
    acresult={}
    for i in d:
        acresult[i[0]]=i[1]
    n = 0 
    maxsenteceweight=0
    maxsentencnum=0
    senteceweight=0
    lastwordindex=0
    for i in acresult:
        if i in range(0+100*n,100+100*n):
            senteceweight += keyword2weight[acresult[i]]
        else:
            if senteceweight>maxsenteceweight:
                maxsenteceweight=senteceweight
                maxsentencnum=n
                lastwordindex=i
            n+=1
            senteceweight = keyword2weight[acresult[i]]
    if senteceweight > maxsenteceweight:
        maxsentencnum = n
        lastwordindex=i
    start=maxsentencnum*100
    end=lastwordindex
    flag = True
    flag2 = True
    while flag:
        if start ==0 or  content[start] in ['。', '？', '！','\n']:
            flag = False
        start -= 1

    while flag2:
        if end>=len(content):
            end=len(content)
            flag2 = False
            break
        if content[end] in ['。', '？', '！','\n']:
            flag2 = False
        end += 1
    
    result = content[start+2:end]
    return result

