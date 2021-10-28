import os,sys,re,time,shutil
import random
import numpy as np
from tfnlp.image_summary.model import ism
from tfnlp.image_summary.image_feature_generator import image_feature_generator 
from tfnlp.image_summary.summary_feature import summary_dict,counter,word_list,word_dict
from tfnlp.image_summary.train_decode_generator import multi_model_state_generator

_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),
                                                 os.path.dirname(__file__), path))


G = multi_model_state_generator(batch_size=128)
def train():
    for i in range(100):
        #ism.load_model()
        for j in range(1000):
            ism.train_decoder(train_generator=G)
        ism.save_model()
        decode()

def decode():
    img224,img299,SL,WID = next(G)
    summary = ism.decode_summary(img224,img299)
    R,C= summary.shape
    for i in range(R):
        I  = WID[i] 
        _I = summary[i]
        sentence = []
        _sentence = []
        for step in range(SL[i]):
            wid  = I[step]
            w = word_list[wid]
            sentence.append(w)
        for step in range(C):
            _wid = _I[step]
            _w = word_list[_wid]
            _sentence.append(_w)
            if _w in ['<NON>', '<END>']:
                break
        print('----------------------------------------')
        print(' '.join(sentence))
        print(' '.join(_sentence))
    print('')
    print('')

if __name__=='__main__':
    if len(sys.argv)<2 or sys.argv[1] == 'train':
        train()
    elif sys.argv[1] == 'test':
        #import pdb;pdb.set_trace()
        decode()
