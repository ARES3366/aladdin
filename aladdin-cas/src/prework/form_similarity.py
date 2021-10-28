#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import json
from xpinyin import  Pinyin
from read_config import predata_path 

# 生成一个词的形近、音近、繁体
"""
    文件说明
    fanti.csv 繁体字
    tongyin.csv 同音字
    xingjin.csv 形近字
"""
d_dict = {"ft": {}, "xj": {}, "yj": {}}

with open("fanti.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = [row for row in reader]

# 繁体
for i, row in enumerate(rows):
    if i != 0:
        j = len(row)
        for d in range(j):
            ro = row[d*2+1:d*2+3]
            if len(ro) and ro[0] != "":
                d_dict["ft"].setdefault(ro[0], {})
                d_dict["ft"][ro[0]] = [ro[1]]

with open("xingjin.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = [row for row in reader]

# 形近
for i, row in enumerate(rows):
    if i != 0:
        words = list(row[1])
        for j in range(int(row[2])):
            d = words.pop(0)
            d_dict["xj"][d] = words
            words.append(d)

pinyin = Pinyin()

# 音近字
with open("tongyin.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = [row for row in reader]

y_dict = dict()
for i, row in enumerate(rows):
    if i != 0:
        py = row[1]
        y_dict.setdefault(py, list())
        y_dict[py].append(row[0])
z_dict = dict()
for k, vs in y_dict.items():
    for v in vs:
        pyin = pinyin.get_pinyin(v, tone_marks='marks')
        z_dict.setdefault(pyin, list())
        z_dict[pyin].append(v)
#
for k, v in z_dict.items():
    # print(k)
    v_len = len(v)
    if v_len < 2:
        continue
    for j in range(v_len):
        d = v.pop(0)
        d_dict["yj"][d] = v
        v.append(d)

# #
# # # d_dict = {k: list(v) for k, v in d_dict.items()}
all_dict = dict()
for ks, vs in d_dict.items():
    for k, v in vs.items():
        all_dict.setdefault(k, set())
        all_dict[k] = all_dict[k] | set(v) | {k}
for ks, vs in all_dict.items():
    all_dict[ks] = list(vs)
    print(ks, vs)
d_dict["all"] = all_dict
json_file = json.dumps(d_dict)

with open(predata_path, "w", encoding="utf-8") as f:
    f.write(json_file)

#
