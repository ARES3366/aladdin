#coding=utf-8
import os,sys,re,time,shutil
import random
import numpy as np
import scipy as sp
# from tensorflow.contrib.keras.api.keras.models import Sequential,Model,load_model
# from tensorflow.contrib.keras.api.keras.layers import Dense,Activation,Reshape
# from tensorflow.contrib.keras.api.keras.layers import Input
# from tensorflow.contrib.keras.api.keras.layers import Conv2D,Flatten
# from tensorflow.contrib.keras.api.keras.layers import MaxPooling2D,AveragePooling2D
# from tensorflow.contrib.keras.api.keras.layers import LocallyConnected2D
# from tensorflow.contrib.keras.api.keras.layers import GRU,LSTM,ConvLSTM2D
# from tensorflow.contrib.keras.api.keras.layers import Embedding
# from tensorflow.contrib.keras.api.keras.layers import Add,Multiply,Average,Maximum,Concatenate,Dot
# from tensorflow.contrib.keras.api.keras.layers import add,multiply,average,maximum,concatenate,dot
# from tensorflow.contrib.keras.api.keras.layers import LeakyReLU,PReLU,ELU,ThresholdedReLU
# from tensorflow.contrib.keras.api.keras.layers import BatchNormalization as BN
# from tensorflow.contrib.keras.api.keras.layers import GaussianNoise,GaussianDropout,AlphaDropout,Dropout
# from tensorflow.contrib.keras.api.keras.layers import TimeDistributed,Bidirectional
# from tensorflow.contrib.keras.api.keras import backend as K
# from tensorflow.contrib.keras.api.keras.utils import plot_model
ctv=('softmax','elu','selu','softplus','softsign','relu','tanh','sigmoid','hard_sigmoid','linear')
metrics=('mae','acc','accuracy')
optimizers=('sgd','adam','rmsprop','adagrad','adadelta','adamax','nadam',)
from acam_dict import WordTree
from wordlist import WordList, Pattern
from zhtools.langconv import *

#采样器
class Sampler():
    def __init__(self,data_dir='traindata',factor=100000):
        cur_path = os.path.dirname(__file__)
        src_path = os.path.dirname(cur_path)
        model_path = os.path.abspath('%s/model'%src_path)
        dic_path = '%s/dict.txt'%model_path
        self.synonym_path = '%s/synonym.txt'%model_path
        self.data_dir=data_dir
        self.factor=factor
        self.synonym_list = self._gen_synonym_list()
        self.word_list = []
        self.word_list_cht = []
        with open(dic_path, 'r', encoding='utf-8') as fp:
            for line in fp:
                w = line[:-1]
                self.word_list.append(w)
                w_cht = Converter('zh-hant').convert(w)
                self.word_list_cht.append(w_cht)
        self.tree = WordTree({'#','@','$'})
        self.tree.build(self.word_list[1:])
        self.tree_cht = WordTree({'#','@','$'})
        self.tree_cht.build(self.word_list_cht[1:])

    def _gen_synonym_list(self):
        with open(self.synonym_path,'r',encoding="utf-8") as fn:
            synonym_list = []
            for line in fn:
                key,words = line.split("$$$$")
                synonym_list.append(words)
        return synonym_list
                            
    def str2vec(self,s):
        vec=np.zeros(70000)
        result,_ = self.tree.search_multi(s)
        for idx in result:
            val = len(result[idx])
            vec[idx] += val
        result,_ = self.tree_cht.search_multi(s)
        for idx in result:
            val = len(result[idx])
            vec[idx] += val
        return self.factor*vec/(0.1+float(len(s)))

    def file2vec(self,fn):
        try:
            with open(fn,'r',encoding="utf-8") as fp:
                s = fp.read()
                return self.str2vec(s)
        except Exception as e:
            print(e)
            return np.zeros(70000)

    def random_file_datas(self):
       files={
              'seqing':[f for f in os.listdir('%s/seqing'%self.data_dir)],
               'zzfd':[f for f in os.listdir('%s/zzfd'%self.data_dir)],
               'other':[f for f in os.listdir('%s/other'%self.data_dir)],
               'normal':[f for f in os.listdir('%s/normal'%self.data_dir)]
       }
       dirs=['seqing' for i in range(2)] + ['zzfd' for i in range(2)]+ ['other' for i in range(1)]+['normal' for i in range(35)]
       for i in range(100000000):
           if i % 100 == 0:
               yield np.zeros(70000), 'normal', 'no_file'
           dirname=random.sample(dirs,1)[0]
           filelist=files[dirname]
           filename=random.sample(filelist,1)[0]
           fn = '%s/%s/%s'%(self.data_dir,dirname,filename)
           yield self.file2vec(fn), dirname, fn

    def order_file_datas(self):
        for dirname in ['normal','zzfd','seqing','other']:
            for filename in [f for f in os.listdir('%s/%s'%(self.data_dir,dirname))]:
                fn = '%s/%s/%s'%(self.data_dir,dirname,filename)
                yield self.file2vec(fn), dirname, fn

    def sample(self,batch,is_random=True):
        list_data=[]
        list_label=[]
        list_filename=[]
        if is_random:
            generator = self.random_file_datas()
        else:
            generator = self.order_file_datas()
        for data,dirname,filename in generator:
            if 'zzfd' in dirname:
                    label=np.array([0,1,0,0])
            elif 'seqing' in dirname:
                    label=np.array([0,0,1,0])
            elif 'other' in dirname:
                    label=np.array([0,0,0,1])
            else:
                    label=np.array([1,0,0,0])
            list_data.append(data[np.newaxis,:])
            list_label.append(label[np.newaxis,:])
            list_filename.append(filename)
            if len(list_label)==batch:
                yield np.concatenate(list_data),np.concatenate(list_label),list_filename
                list_data=[]
                list_label=[]
                list_filename=[]
        yield np.concatenate(list_data), np.concatenate(list_label), list_filename
                                    

#模型
# class NlpModel():
#     def __init__(self,model_file):
#         self.model_file=model_file
#         self.D = self.create_model()

#     def plot_model(self,path):
#         plot_model(self.D, path, show_shapes=True, show_layer_names=True)

#     def create_model(self):
#         try:
#             D=load_model('%s'%self.model_file)
#             return D
#         except:
#             print("h5 file no exists!")
#         i=Input(shape=(70000,))
#         #h=Dense(200,activation='relu')(i)
#         #h=Dense(180,activation='relu')(h)
#         #h=Dense(150,activation='relu')(h)
#         #h=Dense(120,activation='relu')(h)
#         #h=Dense(100,activation='relu')(h)
#         h=Dense(80,activation='relu')(i)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(60,activation='relu')(h)
#         h=Dense(50,activation='relu')(h)
#         h=Dense(30,activation='relu')(h)
#         h=Dense(20,activation='relu')(h)
#         h=Dense(15,activation='relu')(h)
#         h=Dense(10,activation='tanh')(h)
#         o=Dense(4,activation='softmax')(h)
#         D=Model(inputs=i,outputs=o)
#         D.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])
#         return D

            
#     def train(self,data_path='traindata'):
#         i=0
#         sampler=Sampler(data_path)
#         for data,label,_ in sampler.sample(1000):
#             #对样本数据进行小范围随机缩放,使训练后的模型具有一定的容错性
#             data *= random.uniform(0.9,1.1)
#             self.D.train_on_batch(data,label)
#             self.D.save(self.model_file)
#             i+=1
#             if i%2==0:
#                 err,accu=self.D.evaluate(data,label)
#                 print(err,accu)

#     def test(self, data_path='testdata'):
#         #sts是一个统计矩阵:
#         #sts的元素sts[i,j]表示实际标签为i预测标签为j的样本数数量
#         sts = np.zeros([4,4],np.int)
#         err_file_list = []
#         batch_size=1000
#         sampler=Sampler(data_path,factor=50000)
#         for data,label,list_filename in sampler.sample(batch_size,is_random=False):
#             t0=time.time()
#             p_label=self.D.predict(data)
#             t1=time.time()
#             print('----------user time-----',t1-t0)
#             label = np.argmax(label,axis=1)
#             _label = np.argmax(p_label,axis=1)
#             for i in range( label.shape[0] ):
#                 sts[label[i],_label[i]] += 1
#                 if _label[i] != label[i]:
#                     err_file_list.append([label[i],list_filename[i]])       
#             print(sts)
#         return sts, err_file_list
                 
# if __name__ == '__main__':
#     opt = sys.argv[1]
#     model_path = sys.argv[2]
#     data_path = sys.argv[3]
#     model = NlpModel(os.path.abspath(model_path))
#     if opt == 'train':
#         model.train(data_path)
#     elif opt == 'test':
#         sts, err_file_list = model.test(data_path)
#         for idx, filename in err_file_list:
#             print(idx,filename)
#     elif opt == 'pick':
#         sts, err_file_list = model.test(data_path)
#         for idx, filename in err_file_list:
#             print(idx,filename)
#             shutil.move(filename, '%s/not_%s'%(data_path,idx))

