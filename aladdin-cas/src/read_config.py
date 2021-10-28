#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from urllib.parse import quote_plus
import base64
from configparser import ConfigParser
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__), path))

def digit_int_from_env(envname, default=0):
    if envname not in os.environ:
        return default
    s=os.environ[envname]
    if s.isdigit():
        return int(s)
    else:
        return default

def mem_int_from_env(envname, default=100*(2**20)):
    if envname not in os.environ:
        return default
    s=os.environ[envname]
    if s.isdigit():
        return int(s)
    unit = s[-2:]
    val = s[:-2]
    if not val.isdigit():
        return default
    val = int(val)
    if unit  == 'Ki':
        return val*(2**10)
    if unit  == 'Mi':
        return val*(2**20)
    if unit  == 'Gi':
        return val*(2**30)
    else:
        return default

def read_config_infile(section, config_path=""):
    cfg = ConfigParser()
    cfg.read(config_path)
    if section in cfg.sections():
        return cfg[section]
    else:
        cfg[section] = dict()
        return cfg[section]

#service_type 支持四种类型：all、fast-text-analysis、common-classify、image-summary
service_type = os.environ.get('SERVICE_TYPE','all')
server_port = digit_int_from_env('SERVER_PORT', 9528)
predata_path = _get_module_path('predata/similarity_data_list.json')
stopwords_path = _get_module_path('predata/stop_words.txt')
service_code = os.environ.get('service_code','001')

#启用的子工作进程个数.
#默认: 4。
#1个工作进程每秒可以处理75K字/s。对于压力较大的场景可以将适当调高。
worker_processes    = mem_int_from_env('WORKER_PROCESSES',     default = 1)

#每个工作子进程最大允许使用的内存大小，默认4GB
max_mem_use         = mem_int_from_env('MAX_MEM_USE',          default = 4*(2**30))

#最大允许堆积的body字节数：默认为最大内存占用的1/8
max_stock_body_size = mem_int_from_env('MAX_STOCK_BODY_SIZE',  default = max_mem_use/8)

#最大允许处理的单个文本长度
#1024*(2**20)是pandora无负载允许时占用的内存
#max_stock_body_size是分配给多并发下body缓存的内存
#50是根据测试经验得到，处理1M字的文本，会占用50MB的空间大小
max_content_len     = mem_int_from_env('MAX_CONTENT_LEN', default = (max_mem_use-1024*(2**20)-max_stock_body_size)/50)

#为每个请求分配的最大缓存大小
max_buffer_size     = mem_int_from_env('MAX_BUFFER_SIZE', default = 100*(2**20))

#最大的body大小, 默认是最大允许堆积body字节数。
max_body_size       = mem_int_from_env('MAX_BODY_SIZE',   default = max_stock_body_size)

#mongo配置与milvus配置
config_path = os.environ.get("config_path", "/root/server.conf")
mongodb_conf = read_config_infile("mongodb", config_path=config_path)
mongo_config = dict(
    host=mongodb_conf.get('host', "aladdin-cas-mongo").replace('"', ''),
    port=int(mongodb_conf.get('port', "27017").replace('"', '')),
    db_auth=mongodb_conf.get("db_auth", "admin").replace('"', ''),
    db=mongodb_conf.get("db", "aladdin-cas").replace('"', ''),
    user=quote_plus(mongodb_conf.get("user", "").replace('"', '')),
    password=quote_plus(mongodb_conf.get("password", "").replace('"', '')),
    replicaSet=quote_plus(mongodb_conf.get("replicaSet", "").replace('"', '')),
    sslCAFile=quote_plus(mongodb_conf.get("sslCAFile", "").replace('"', '')),
    ssl=quote_plus(mongodb_conf.get("ssl", "").replace('"', '')),
    options=mongodb_conf.get("options", str(dict())).strip(),
)
milvus_config = dict(
    host=os.environ.get('milvus_host','127.0.0.1'),
    port=os.environ.get('milvus_port',19530),
)
# milvus_od_collection = os.environ.get("milvus_od_collection", "object_detection")
# mongo_od_collection = os.environ.get("mongo_od_collection", "object_detection")
#用于敏感文件标记的mysql配置

mysql_config = dict(
    host=os.environ.get('mysql_host','127.0.0.1'),
    port=int(os.environ.get('mysql_port', 3306)),
    user=quote_plus(os.environ.get('mysql_user','root')),
    db='atf_db',
    password=quote_plus(os.environ.get('mysql_password', '123456')),
    #charset='utf8'
)

tfserving_config = dict(
    tfserving_host=os.environ.get("tfserving_host", "127.0.0.1"),
    tfserving_port=os.environ.get("tfserving_port", "8500")
)

globalization_lang = "en_US"

# exception_level
# 0 code, message, cause, detail
# 1 code, message, cause
# 2 code, message
# 3 code, cause, detail
# 4 code, cause
exception_level = int(os.environ.get("exception_level", 0))

# 目标检测的阈值
detection_confidence_threshold = float(os.environ.get("detection_confidence_threshold", 0.6))
#tfserving 目标检测模型名称
detection_model_name= os.environ.get("detection_model_name", "detection")
#tfserving 图像分类模型名称
classify_model_name= os.environ.get("classify_model_name", "fbnetv2")

elasticsearch_conf = read_config_infile("elasticsearch", config_path=config_path)
elasticsearch_config = dict(
    host=elasticsearch_conf.get('host', "aladdin-cas-es").replace('"', ''),
    port=int(elasticsearch_conf.get('port', "9200").replace('"', '')),
    aliases=elasticsearch_conf.get('aliases', "delg").replace('"', ''),
    index_num=int(elasticsearch_conf.get('index_num', "128").replace('"', '')),
    index_type=int(elasticsearch_conf.get('index_type', "0").replace('"', '')),
)

dl_inference_server_conf = read_config_infile("dl-inference-server", config_path=config_path)
dl_inference_server_config = dict(
    host=dl_inference_server_conf.get('host', "aladdin-cas-dl").replace('"', ''),
    port=int(dl_inference_server_conf.get('port', "8500").replace('"', '')),
)

delg_conf = read_config_infile("delg-codebook", config_path=config_path)
delg_config = dict(
    global_path_1=delg_conf.get("global_path_1", "").replace('"', ''),
    global_path_2=delg_conf.get("global_path_2", "").replace('"', ''),
    local_path_1=delg_conf.get("local_path_1", "").replace('"', ''),
    local_path_2=delg_conf.get("local_path_2", "").replace('"', ''),
)
