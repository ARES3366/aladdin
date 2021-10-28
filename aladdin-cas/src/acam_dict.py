# coding: utf-8
from __future__ import absolute_import
import json, re
import gc
from collections import deque, defaultdict
#from wordlist import *
#from wordlist import Pattern,WordList
#from wordlist import get_word_list


#get_word_list = get_word_list
#Pattern = Pattern
#WordList = WordList


class ACAMExp(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)

    def __repr__(self):
        return "ACAMExp: %s" % super(ACAMExp, self).__repr__()


class Node(object):
    def __init__(self, value):
        self.value = value
        self.children = dict()
        self.par = None
        self.tag = None
        self.fail = None
        self.weight = 1
        self.length = 0

    def add_child(self, child):
        if not isinstance(child, Node):
            return

        self.children[child.value] = child
        child.par = self


class WordTree(object):
    '''
     修改
    '''
    def __init__(self, filter_set=None, predata_file=None):
        self.root = Node(0)
        self.len = 0
        if filter_set == None:
            filter_set=set()
        self.filter_set = filter_set
        self.predata_file = predata_file
        self.sim_data = defaultdict(list)
        self.kv_data = dict()
        self.filter_pattern = None
        if len(filter_set) > 0:
            s_pattern = '[%s]'%''.join(list(self.filter_set))
            self.filter_pattern = re.compile(s_pattern)
            

    @staticmethod
    def __dftraverse(node, func=None):
        if not isinstance(node, Node):
            return

        if func:
            func(node)

        for c in node.children:
            WordTree.__dftraverse(c)

    def dftraverse(self, func=None):
        """
        深度优先变量树
        :param func: 遍历时执行的操作
        :return:
        """

        def print_v(node):
            if node is self.root:
                print('Root->')
            else:
                print(node.value)

        WordTree.__dftraverse(self.root, print_v if not func else func)

    @staticmethod
    def __bftraverse(traverse_queue, func):
        while len(traverse_queue):
            node = traverse_queue.popleft()

            if not isinstance(node, Node):
                return

            if func:
                func(node)

            for child in node.children.values():
                # next_queue.append(child)
                traverse_queue.append(child)

    def bftraverse(self, func=None):
        """
        广度优先变量树
        :param func: 遍历时需要进行的操作，默认传入参数 Node 类型的变量
        :return:
        """
        def print_v(node):
            if node.par is None:
                print('Root->')
            else:
                print(node.value)

        queue = deque()
        queue.append(self.root)
        WordTree.__bftraverse(queue, print_v if not func else func)

    def __add_word(self, word, tag):
        # if not isinstance(word, str):
        #     raise ACAMExp("Word type not allowed!")

        # 　从 root 节点开始搜索
        cur = self.root
        for c in word:
            if not cur.children:
                new = Node(c)
                cur.add_child(new)
                cur = new
            else:
                # found = False

                node = cur.children.get(c)

                if node:
                    cur = node
                    continue
                else:
                    new = Node(c)
                    cur.add_child(new)
                    cur = new

        # 设置一个 tag
        if tag is not None:
            cur.tag = tag
            cur.length = len(word)

        self.len += 1

    def build(self, wlist):
        """
        增量方式添加词语
        :param wlist: 待添加的词
        :return:
        """
        # 首先构建
        for i in range(len(wlist)):
            if isinstance(wlist[i], list):
                word = wlist[i][0]
            else:
                word = wlist[i]

            self.__add_word(word, i)

        # 构建 AC 自动机
        def find_failure(node):
            # 1. 根节点，不做处理
            if node is self.root:
                return

            # 2. 第二层节点，全部指向 root
            if node.par is self.root:
                node.fail = self.root
                return

            # 3. 其他节点，搜索
            node_to_search = node.par.fail
            while True:
                fail = node_to_search.children.get(node.value)
                if fail:
                    node.fail = fail
                    break
                else:
                    if node_to_search == self.root:
                        node.fail = self.root
                        break
                    else:
                        node_to_search = node_to_search.fail

        WordTree.bftraverse(self, find_failure)

    def search_one(self, word):
        """
        查询一个关键词
        :param word: 关键词
        :return: 关键词在 word_list 中的位置
        """

       
         # 把next修改为nex 
        
        cur = self.root
        failed = False
        for c in word:
            nex = cur.children.get(c)
            if nex is None:
                failed = True
                break
            else:
                cur = nex

        if not failed and cur.tag!=None:
            return cur.tag

        return -1

    def search_multi(self, text):
        """
        查找多个匹配的模式
        :param text: 待处理字符串
        :return:
        """
        filter_loc_set = set()
        cur = self.root
        result = dict()
        for i in range(len(text)):
            if text[i] in self.filter_set:
                filter_loc_set.add(i)
                continue
            step_failed = True

            while True:
                node = cur.children.get(text[i])
                if node:
                    cur = node
                    step_failed = False

                if not step_failed:
                    if cur.tag is not None:
                        if cur.tag in result:
                            result[cur.tag].append(i)
                        else:
                            # 记录出现位置
                            result[cur.tag] = [i]
                    tp = cur.fail
                    while tp:
                        if tp.tag is not None:
                            if tp.tag in result:
                                result[tp.tag].append(i)
                            else:
                                result[tp.tag] = [i]
                        tp = tp.fail

                    break
                else:
                    if cur.fail:
                        cur = cur.fail

                    else:
                        break

        return result, filter_loc_set

    def search_multi_fuzzy(self, text, result, bitmap=None):
        if len(self.sim_data) == 0 and self.predata_file is not None:
            with open(self.predata_file, "r",encoding="utf-8") as f:
                json_content = f.read()
                self.kv_data = json.loads(json_content)
                json_content = None
                gc.collect()
                self.sim_data = self.kv_data["all"]

                # for kvdata in self.kv_data.values():
                #     for k, v in kvdata.items():
                #         self.sim_data[k] += v

        text_len = len(text)

        for i, x in enumerate(text):
            if bitmap and bitmap.get_one(i):
                continue
            if text[i] in self.filter_set:
                continue
            cur = self.root

            if x in self.sim_data:
                que = set(cur.children.keys()) & set(self.sim_data[x])
            else:
                que = set(cur.children.keys()) & {x}
            que_list = deque()
            #修改
            [que_list.append((cur.children[q], i+1)) for q in que]
            while len(que_list):
                d = que_list.popleft()
                ie = d[1]
                qe = d[0]
                while ie < text_len:
                    if text[ie] in self.filter_set:
                        ie += 1
                    else:
                        break
                if ie >= text_len:
                    break
                s_ie = text[ie]
                if s_ie in self.sim_data:
                    xq = set(qe.children.keys()) & set(self.sim_data[s_ie])
                else:
                    xq = set(qe.children.keys()) & {s_ie}
                # xq = set(qe.children.keys()) & set(self.sim_data.get(s_ie, [])+[s_ie])
                for xe in xq:
                    if qe.children[xe].tag is not None:
                        result.setdefault(qe.children[xe].tag, list())
                        result[qe.children[xe].tag].append(ie)
                    que_list.append((qe.children[xe], ie+1))

        return result

    def search_cut(self, text):
        """
        查找多个匹配的模式
        :param text: 待处理字符串
        :return:
        """
        if self.filter_pattern:
            text = self.filter_pattern.sub('',text)
        cur = self.root
        result = set()
        for i in range(len(text)):
            step_failed = True

            while True:
                node = cur.children.get(text[i])
                if node:
                    cur = node
                    step_failed = False

                if not step_failed:
                    if cur.tag is not None:
                        result.add(i)
                        result.add(i-cur.length)
                        cur = self.root
                        break
                    tp = cur.fail
                    while tp:
                        if tp.tag is not None:
                            result.add(i)
                            result.add(i-cur.length)
                            cur = self.root
                            break
                        tp = tp.fail
                    break
                else:
                    if cur.fail:
                        cur = cur.fail

                    else:
                        break

        pos = 0
        for i in sorted(list(result)):
            if i < pos:
                continue
            else:
                yield text[pos:i+1]
                pos = i+1


