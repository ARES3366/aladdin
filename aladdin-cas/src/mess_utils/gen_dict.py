import os,sys
from collections import Counter

counter=Counter()

for fn in sys.argv[1:]:
    with open(fn, 'r') as fp:
        for line in fp:
            counter.update(line[:-1])
        

cht_list = [x for x,n in counter.items()]          
cht_list.sort(key=lambda x : counter[x], reverse=True)

with open('dcit.txt', 'w') as fw:
    for c in counter:
        fw.write('%s\n'%c)
     
