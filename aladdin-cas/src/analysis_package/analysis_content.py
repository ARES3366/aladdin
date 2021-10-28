#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
from collections import defaultdict
from xpinyin import Pinyin
from utils import BitMap
from read_config import predata_path
from acam_dict import WordTree

def match_keywords(content, words, tree=None):
    if tree == None:
        tree = WordTree(filter_set={})#{"*", "?", "$", "#", "@", "!", " "})
        tree.build(words)
    content_len = len(content)
    r, _ = tree.search_multi(content)
    word_locate = dict()
    for word_id in r:
        word = words[word_id]
        word_locate[word]=[]
        seg_list = ['，','。','！', '：','“', "”", "；", "\n", "\t"]
        for pos in r[word_id]:
            pos_left, pos_right = pos-len(word)+1, pos
            for i in range(50):
                pos_left -= 1
                if pos_left < 0 or content[pos_left] in seg_list:
                    break
            for j in range(50):
                pos_right += 1
                if pos_right==content_len:
                    break
                if content[pos_right] in seg_list:
                    if content[pos_right] == '\n' and content[pos_right-1] == '\r':
                        pos_right -= 1
                    break
            near_str = content[pos_left+1:pos_right]
            if near_str not in word_locate[word]:
                word_locate[word].append(near_str)
            if len(word_locate[word])==100:
                break
    return word_locate

