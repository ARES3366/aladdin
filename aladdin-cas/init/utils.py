import os
import base64
from pymongo import MongoClient
from urllib.parse import quote_plus
from configparser import ConfigParser


def get_mongo_client(mongo_config):
    uri_pre = "mongodb://"
    uri_auth = mongo_config["user"] + ":" + mongo_config["password"] + "@"
    host = mongo_config["host"]
    port = mongo_config["port"]
    host_list = host.split(",")
    _list = [x + ":" + str(port) for x in host_list]
    uri_host_port = ",".join(_list)
    if (mongo_config["user"] and mongo_config["password"]):
        uri_auth = mongo_config["user"] + ":" + mongo_config["password"] + "@"
        uri_pre = uri_pre + uri_auth
    uri_host_port = uri_host_port + "/" + mongo_config["db_auth"]
    params_map = dict(
        replicaSet=str(mongo_config["replicaSet"]), 
        ssl=str(mongo_config["ssl"]), 
        sslCAFile=str(mongo_config["sslCAFile"]))
    params_list = [f"{quote_plus(k)}={quote_plus(v)}" for k,v in params_map.items() if bool(v)]
    if not params_list:
        uri = uri_pre + uri_host_port
    else:
        uri = uri_pre + uri_host_port + "?" + "&".join(params_list)
    if mongo_config["options"] == '{}':
        pass
    else:
        options = mongo_config["options"]
        options = [i.split(":") for i in options.replace('"', '').split("\n")]
        options = [(i[0].strip(), i[1].strip()) for i in options]
        options = [f"{quote_plus(i[0])}={quote_plus(i[1])}" for i in options if i[1] not in ['', 'null']]
        options = "&".join(options)
        if bool(options):
            uri = uri + "&" + options
    print(uri)
    return MongoClient(uri), uri

def read_config_infile(section, config_path=""):
    cfg = ConfigParser()
    cfg.read(config_path)
    if section in cfg.sections():
        return cfg[section]
    else:
        cfg[section] = dict()
        return cfg[section]

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
print(mongo_config)

milvus_conf = read_config_infile("milvus", config_path=config_path)
milvus_config = dict(
    host=milvus_conf.get('host', "aladdin-cas-milvus").replace('"', ''),
    port=int(milvus_conf.get('tcpPort', "19530").replace('"', '')),
)
print(milvus_config)

mysql_conf = read_config_infile("mysql", config_path=config_path)
mysql_config = dict(
    host=mysql_conf.get('host','aladdin-cas-mysql').replace('"', ''),
    port=int(mysql_conf.get('port', "3306").replace('"', '')),
    user=quote_plus(mysql_conf.get('user','root')).replace('"', ''),
    password=quote_plus(mysql_conf.get('password', '123456')).replace('"', ''),
)
print(mysql_config)

es_conf = read_config_infile("elasticsearch", config_path=config_path)
es_config = dict(
    host=es_conf.get('host', "aladdin-cas-es").replace('"', ''),
    port=int(es_conf.get('port', "9200").replace('"', '')),
    aliases=es_conf.get('aliases', "delg").replace('"', ''),
    index_num=int(es_conf.get('index_num', "128").replace('"', '')),
    index_type=int(es_conf.get('index_type', "0").replace('"', '')),
)