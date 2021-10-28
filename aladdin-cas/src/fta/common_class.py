import os
import numpy as np
import jieba
from utils import singleton
from client.tfs_client import BaseClient
from protos.tensorflow.core.framework import types_pb2
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__), path))

# from TFS_client import inference_sync

@singleton
class Content2Vec():
    def __init__(self, num_label=2, num_step=1000, dict_path=_get_module_path('../dic/ccd.txt')):
        self.dict_path = dict_path
        self.num_label = num_label
        self.num_step=num_step
        self.word_dict = self.load_dict()
        self.num_words = len(self.word_dict)

    def load_dict(self):
        if self.dict_path:
            jieba.load_userdict(self.dict_path)
        wid = 0
        wd = {}
        for w,freq in jieba.dt.FREQ.items():
            if freq > 0:
                wd[w] = wid
                wid += 1
        return wd

    def process_text(self, content):
        #先进行分词  
        words = list(jieba.cut(content, cut_all=True))[:self.num_step]
        return self.process_word_list(words)

    def process_word_list(self,words):
        #初始化向量序列  
        data = [0 for i in range(self.num_step)] 
        #按照词序，依次把用词向量填充序列  
        for i in range(len(words)):
            w = words[i]  
            if w in self.word_dict:  
                data[i] = self.word_dict[w]
        return data

def do_commom_class(wordlist):
    all_word = []
    for w0 in wordlist:
        for w1 in w0:
            all_word.append(w1[0])

    lf = Content2Vec()
    da = lf.process_word_list(all_word[:1000])
    d=np.array([da])
    data = np.expand_dims(d, axis=0).astype(np.int32).reshape((-1,1000))
    # bc = BaseClient()
    # result = bc.inference("only_attention", "serving_default", "text", data, tf.int32)
    # 得到的result是protobuf的格式，因此我们需要如下形式提取出向量
    model_name = "only_attention"
    signature_name = "serving_default"
    input_data = {
        "text":{
            "data": data,
            "dtype": types_pb2.DT_INT32
        }
    }
    output_list = ["class_prob"]
    tfs_serving = BaseClient()

    out = tfs_serving.inference_sync(model_name,signature_name,input_data,output_list)
    # print(out)
    val=np.array(out['class_prob']['value'])

    # train_data_dir=_get_module_path('../tfnlp/data/THUCNews')
    # label_list = os.listdir(train_data_dir)
    label_list=['体育', '娱乐', '家居', '彩票', '房产', '教育', '时尚', '时政', '星座', '游戏', '社会', '科技', '股票', '财经']
    final_prob=np.array(val)
    label_id = np.argmax(final_prob)
    label_name = label_list[label_id]
    return label_name

