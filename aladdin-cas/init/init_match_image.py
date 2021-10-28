import os, time
import json
import requests
from utils import es_config


def init_match_image_es():
    try:
        host = es_config["host"]
        port = es_config["port"]
        aliases = es_config["aliases"]
        number = es_config["index_num"]
        _type = es_config["index_type"]
        for i in range(number):
            url = f'http://{host}:{port}/{aliases}_{i}'
            data = {
                "mappings": {
                    _type : {
                        "properties" : {
                            "label" : {
                                "type" : "keyword",
                            },
                            "vid" : {
                                "type" : "integer",
                            },
                        },
                    },
                },
            }
            t1 = time.time()
            res = requests.put(url=url, json=data)
            print(f'Status: {res.status_code}  Processed 1 query InitIndex in {time.time() - t1} seconds')
            print(res.text)

        url = f'http://{host}:{port}/_aliases'
        
        data = {
            "actions": [],
        }
        for i in range(0, number):
            data["actions"].append({"add": {"index": f"{aliases}_{i}", "alias": f"{aliases}"}})
        t1 = time.time()
        res = requests.post(url=url, json=data)
        print(f'Status: {res.status_code}  Processed 1 query InitAliases in {time.time() - t1} seconds')
        print(res.text)

        return True

    except Exception as e:
        print(e)
        return False

def init_match_image():
    x = 1
    while True:
        print("=="*14 + " Ready to Init ElasticSearch In Match-Image : {} ".format(x) + "=="*14)
        res = init_match_image_es()
        if res:
            print("=="*14 + " Successfully Initialized ElasticSearch In Match-Image " + "=="*14 + "\n\n")
            break
        else:
            print("=="*14 + " Failed Initialization ElasticSearch In Match-Image " + "=="*14 + "\n\n")
            print("Sleep for {ti} minutes and try again : {tim} times.".format(ti=5*x, tim=x))
            time.sleep(300*x)
            continue

if __name__ == "__main__":
    init_match_image()
