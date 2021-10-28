#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,time

import unittest
from acam_dict import WordTree
from wordlist import WordList, Pattern
from utils import build_dictionary, BitMap

class TestUtils(unittest.TestCase):

    def test_build_dictionary(self):
        cur_dir = os.path.dirname(os.path.realpath(__file__))
        dic_path = "%s/test_dic"%cur_dir
        predata_path = os.path.abspath('%s/../src/predata'%cur_dir)
        t0=time.time()
        wl, tree = build_dictionary(dic_path, predata_path)
        t1=time.time()
        print('-----------------------',t1-t0)
        #self.assertEqual(len(word_list), 68480)
        with open('%s/黄金渔村.txt'%cur_dir, 'r') as fp:
            s = fp.read()
        t0=time.time()
        res, ls = tree.search_multi(s)
        t1=time.time()
        print('-----------------------',t1-t0)
        
