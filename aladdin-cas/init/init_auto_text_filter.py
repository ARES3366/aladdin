from utils import get_mongo_client, mongo_config, milvus_config
from time import sleep
from milvus import Milvus, IndexType, MetricType, Status
from pymongo import DESCENDING, ASCENDING


def init_auto_text_filter_milvus():
    
    collection_name = "atf"
    try:
        print("Name of Milvus' Collection : {} ".format(collection_name))
        milvus = Milvus(host=milvus_config["host"], port=milvus_config["port"])

        param = {
            'collection_name': collection_name, 
            'dimension': 5000, 
            'index_file_size': 1024, 
            'metric_type': MetricType.IP
        }
        print(param)
        milvus.create_collection(param)
      
        ivf_param = {"m": 64, "nlist": 1000}
        milvus.create_index(collection_name, IndexType.IVF_PQ, ivf_param)
        return True

    except Exception as e:
        print(e)
        return False

def init_auto_text_filter():
    # x = 1
    # while True:
    #     print("=="*14 + " Ready to Init MongoDB In Auto-text-filter : {} ".format(x) + "=="*14)
    #     res = init_face_recognition_mongodb()
    #     if res:
    #         print("=="*14 + " Successfully Initialized MongoDB In Auto-text-filter " + "=="*14 + "\n\n")
    #         break
    #     else:
    #         print("=="*14 + " Failed Initialization MongoDB In Auto-text-filter " + "=="*14 + "\n\n")
    #         print("Sleep for {ti} minutes and try again : {tim} times.".format(ti=5*x, tim=x))
    #         sleep(300*x)
    y = 1
    while True:
        print("=="*14 + " Ready to Init Milvus In Auto-text-filter : {} ".format(y) + "=="*14)
        res = init_auto_text_filter_milvus()
        if res:
            print("=="*14 + " Successfully Initialized Milvus In Auto-text-filter " + "=="*14 + "\n\n")
            break
        else:
            print("=="*14 + " Failed Initialization Milvus In Auto-text-filter " + "=="*14 + "\n\n")
            print("Sleep for {ti} minutes and try again : {tim} times.".format(ti=5*y, tim=y))
            sleep(300*y)
            y += 1
            continue

if __name__ == "__main__":
    init_auto_text_filter()
