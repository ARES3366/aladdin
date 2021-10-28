import os,sys,re,time,shutil
import random
import numpy as np
from tfnlp.image_summary.image_feature_generator import image_data_generator, image_feature_generator 
from tfnlp.image_summary.summary_feature import summary_dict,counter,word_list,word_dict

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))

def multi_model_state_generator(batch_size=64):
    img224_list = []
    img299_list = []
    summary_list = []
    SL_list = []
    for file_name, img224, img299 in image_feature_generator():
        if file_name not in summary_dict:
            continue
        #从5个摘要中随机选取一个摘要
        summary = dict(random.sample(summary_dict[file_name],1)[0])
        summary = summary[:100-1]
        summary_data = np.zeros([1,100],dtype=np.int64)
        for SL in range(len(summary)):
            w = summary[SL]
            wid = word_dict[w] if w in word_dict else word_dict['<UKN>']
            summary_data[0,SL] = wid
        summary_data[0,SL+1] = word_dict['<END>']
        summary_list.append(summary_data)
        SL_list.append(2+SL)
        img224_list.append(img224[np.newaxis,:])
        img299_list.append(img299[np.newaxis,:])
        if len(img224_list)==batch_size:
            #SL = np.clip(SL, 0, max_val)
            yield np.concatenate(img224_list), \
                  np.concatenate(img299_list), \
                  np.array(SL_list), \
                  np.concatenate(summary_list)
            img224_list=[]
            img299_list=[]
            summary_list=[]
            SL_list=[]
