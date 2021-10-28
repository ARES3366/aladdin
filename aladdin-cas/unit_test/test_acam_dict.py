#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,time

import unittest
from acam_dict import Node, WordTree
from wordlist import WordList, Pattern

class TestNode(unittest.TestCase):
    def test_add_child(self):
        node = Node(value = '中')
        child1 = Node(value = '国')
        child2 = Node(value = '间')
        child3 = Node(value = '华')
        node.add_child(child1)
        node.add_child(child2)
        node.add_child(child3)
        self.assertIn('国', node.children)
        self.assertIn('间', node.children)
        self.assertIn('华', node.children)
     

class TestWordTree(unittest.TestCase):
    def test_dftraverse(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        predata_path = os.path.abspath('%s/../src/predata'%cur_dir)
        wt = WordTree(filter_set={'#','@','$'}, predata_file=predata_path)
        wt.build(wlist=['中国','中华','中间'])
        wt.dftraverse()

    def test_search_one(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        predata_path = os.path.abspath('%s/../src/predata'%cur_dir)
        wt = WordTree(filter_set={'#','@','$'}, predata_file=predata_path)
        wt.build(wlist=['中国','中华','中间'])
        tag = wt.search_one('中国')
        self.assertEqual(tag, 0)
        tag = wt.search_one('中国人')
        self.assertEqual(tag, -1)

    def test_search_multi(self):
        wt = WordTree(filter_set={'@','#'}, predata_file=None)
        wt.build(wlist=['中华','人民','共和国'])
        text = '''中@华人#民#人@民@共@和#国'''
        result, filter_loc_set = wt.search_multi(text)
        self.assertEqual([2], result[0])
        self.assertEqual([5,9], result[1])
        self.assertEqual([15], result[2])
        #字符‘@’，‘#’出现在text的真实位置与函数返回结果是否一致
        self.assertEqual({1,4,6,8,10,12,14}, filter_loc_set)

    def test_search_multi_fuzzy(self):
        if True:
            return
        wt = WordTree(filter_set={'@','#'}, predata_file=None)
        wt.build(wlist=['背景','适中','北京市'])
        text = '''北京是中国的首都'''
        result,_ = wt.search_multi(text)
        result = wt.search_multi_fuzzy(text, result)
        self.assertEqual([1], result[0])
        self.assertEqual([3], result[1])
        self.assertEqual([2], result[2])

    def test_search_cut(self):
        wt = WordTree(filter_set={'@','#','$'}, predata_file=None)
        wt.build(wlist=['中华','人民','共和国', '华人','海外','公民'])
        text = '''海$#外$$华@@人不$是中#华#人@民@共@和#国@的#公###民'''
        result = wt.search_cut(text)
        for w in result:
            print(w)
            
