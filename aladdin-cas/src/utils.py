#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from acam_dict import WordTree
from wordlist import WordList, Pattern
import threading
def singleton(cls):
    instances = {}
 
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
 
    return wrapper




def newsingleton_1(cls):
    lock_ = threading.Lock()

    def make_singleton(*args, **kwargs):
        if not hasattr(cls, '_instance'):
            with lock_:
                if not hasattr(cls, '_instance'):
                    cls._instance = cls(*args, **kwargs)
        return cls._instance

    return make_singleton

def newsingleton(cls):
    lock_ = threading.Lock()
    instances = {}
    def wrapper(*args, **kwargs):
        with lock_:
            flag = args[0]
            if cls not in instances:
                instances[cls] = {flag: cls(*args, **kwargs)}
            elif cls in instances:
                tmp_cls = instances[cls]
                if flag not in tmp_cls:
                    instances[cls][flag] = cls(*args, **kwargs)
            else:
                pass
        return instances[cls][flag]
    return wrapper

def build_dictionary(dic_path, predata_path):
    word_list = WordList(os.path.join(os.path.dirname(__file__),
                                      dic_path),
                         Pattern(1, '\t', True), predata_path)
    filter_character_set = {"*", "?", "$", "#", "@", "!", " "}
    tree = WordTree(filter_character_set, predata_path)
    tree.build(word_list)

    return word_list, tree


def request_handler(func):
    def deal_funt(*args, **kwargs):

        try:
            obj = func(*args, **kwargs)
            if isinstance(obj, dict):
                obj["status"] = 0
                args[0].write(obj)
        except Exception as e:
            errmsg = e
            error = {
                'status': 1,
                'errcode': 110,
                'errmsg': errmsg,
            }
            args[0].write(error)

    return deal_funt


class BitMap(object):

    def __init__(self, maxsize):
        self.size = (maxsize+31-1)//31
        self.array = [0 for i in range(self.size)]

    def bitindex(self, num):
        return num % 31

    def set_one(self, num):
        array_index = num // 31
        bit_index = self.bitindex(num)
        ele = self.array[array_index]
        self.array[array_index] = ele | 1 << bit_index

    def get_one(self, num):
        array_index = num // 31
        bit_index = self.bitindex(num)
        ele = self.array[array_index]
        if ele & (1 << bit_index):
            return True
        else:
            return False

