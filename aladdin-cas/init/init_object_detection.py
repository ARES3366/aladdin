from utils import get_mongo_client, mongo_config, milvus_config
from time import sleep
from milvus import Milvus, IndexType, MetricType, Status

def init_object_detection_mongodb():
    try:
        print(mongo_config)
        client, _ = get_mongo_client(mongo_config)
        db = client[mongo_config["db"]]
        db["object_detection"].create_index("url")
        db["object_detection"].create_index("vid")
        db["tbl_face_info"].drop()
        return True
    except Exception as e:
        print(e)
        return False

def init_object_detection_milvus():
    
    collection_name = "object_detection"
    try:
        print("Name of Milvus' Collection : {} ".format(collection_name))
        milvus = Milvus(host=milvus_config["host"], port=milvus_config["port"])
        
        param = {
            'collection_name': collection_name, 
            'dimension': 128, 
            'index_file_size': 1024, 
            'metric_type': MetricType.L2
        }
        milvus.create_collection(param)
        
        for i in range(1000):
            milvus.create_partition(collection_name, str(i))

        ivf_param = {"m": 16, "nlist": 1024}
        milvus.create_index(collection_name, IndexType.IVF_PQ, ivf_param)
        return True

    except Exception as e:
        print(e)
        return False
def init_face_recognition_milvus():

    collection_name = "face_recognition"
    try:
        print("Name of Milvus' Collection : {} ".format(collection_name))
        milvus = Milvus(host=milvus_config["host"], port=milvus_config["port"])

        param = {
            'collection_name': collection_name, 
            'dimension': 128, 
            'index_file_size': 1024, 
            'metric_type': MetricType.L2
        }
        milvus.create_collection(param)

        ivf_param = {"m": 16, "nlist": 1024}
        milvus.create_index(collection_name, IndexType.IVF_PQ, ivf_param)
        return True

    except Exception as e:
        print(e)
        return False

def init_object_detection():
    x = 1
    while True:
        print("=="*14 + " Ready to Init MongoDB In Object Detection : {} ".format(x) + "=="*14)
        res = init_object_detection_mongodb()
        if res:
            print("=="*14 + " Successfully Initialized MongoDB In Object Detection " + "=="*14 + "\n\n")
            break
        else:
            print("=="*14 + " Failed Initialization MongoDB In Object Detection " + "=="*14 + "\n\n")
            print("Sleep for {ti} minutes and try again : {tim} times.".format(ti=5*x, tim=x))
            sleep(300*x)
            continue
    y = 1
    while True:
        print("=="*14 + " Ready to Init Milvus In Object Detection : {} ".format(y) + "=="*14)
        res = init_object_detection_milvus()
        if res:
            print("=="*14 + " Successfully Initialized Milvus In Object Detection " + "=="*14 + "\n\n")
            break
        else:
            print("=="*14 + " Failed Initialization Milvus In Object Detection " + "=="*14 + "\n\n")
            print("Sleep for {ti} minutes and try again : {tim} times.".format(ti=5*y, tim=y))
            sleep(300*y)
            continue
    while True:
        print("=="*14 + " Ready to Init Milvus In Object Detection : {} ".format(y) + "=="*14)
        res = init_face_recognition_milvus()
        if res:
            print("=="*14 + " Successfully Initialized Milvus In Object Detection " + "=="*14 + "\n\n")
            break
        else:
            print("=="*14 + " Failed Initialization Milvus In Object Detection " + "=="*14 + "\n\n")
            print("Sleep for {ti} minutes and try again : {tim} times.".format(ti=5*y, tim=y))
            sleep(300*y)
            continue

if __name__ == "__main__":
    init_object_detection()
