import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import pymongo
from read_config import mongo_config
from utils import singleton
from urllib.parse import quote_plus

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
    return AsyncIOMotorClient(uri)

@singleton
class MongoDBClient(object):
    def __init__(self):
        self.client = get_mongo_client(mongo_config)
        self.database = self.client[mongo_config.get("db","aladdin_cas")]
        self.collection = self.database["object_detection"]
    
    async def count(self, conditions=None):
        if conditions:
            n = await self.collection.count_documents(conditions)
        else:
            n = await self.collection.count_documents({})
        return n

    async def insert(self, value=None):
        insert_document = None
        if value:
            insert_document = dict(vid=value["vid"], url=value["url"], position=value["position"], classify=value["classify"], top_10_partition=value["top_10_partition"], areas=value["areas"])
        result = await self.collection.insert_one(insert_document)

    async def insert_many(self, values):
        lens_of_values = len(values)
        if lens_of_values > 0:
            result = await self.collection.insert_many(values)
            
            if result.acknowledged is True and len(result.inserted_ids) == lens_of_values:
                return dict(message=result, status=0)
            else:
                return dict(status=1,message="not all documents was successfully inserted")
        else:
            return dict(status=1, message="insert data is null")
        

    async def delete_one(self, conditions=None):
        if conditions:
            result = await self.collection.delete_one(conditions)
            return dict(delete_num=result.deleted_count, status=0)
        else:
            return dict(delete_num=0, status=1)
    async def delete_many(self, conditions=None):
        if conditions:
            result = await self.collection.delete_many(conditions)
            return dict(delete_num=result.deleted_count, status=0)
        else:
            return dict(delete_num=0, status=1)

    async def select(self, conditions=None):
        result_list = []
        if conditions:
            async for document in self.collection.find(conditions):
                result_list.append(document)
        else:
            async for document in self.collection.find({}):
                result_list.append(document)
        return result_list

    async def select_one_and_update(self, conditions=None):
        result =  await self.collection.find_one_and_update(conditions["find"], conditions["update"], return_document=True) 
        return result

    async def select_sorted(self, conditions=None, key=None, count=None):
        result_list = []
        if count:
            async for document in self.collection.find(conditions).sort(str(key), pymongo.DESCENDING).limit(count):
                result_list.append(document)
        else:
            async for document in self.collection.find(conditions).sort(str(key), pymongo.DESCENDING):
                result_list.append(document)
        return result_list
