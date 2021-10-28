import asyncio
import aiohttp
import traceback
import json
import numpy as np
from match_image.utils import *
from match_image.extractor import FeatureExtractor
from exception_handler import InternalErrorException


GetVisualLabels = FeatureExtractor(MODEL_CONFIG)

async def SearchImageLabels(image):
    # Generate hash's value by gray image
    try:
        hash_value = AverageHash(image, 64)
    except:
        cause = "Picture Format Error."
        error_detail = {
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

    # Search image's labels by hash's value
    try:
        url = "{0}/{1}/_search?q=_id:{2}".format(
            ELASTICSEARCH_PATH,
            ALIASES,
            hash_value,
        )
        async with aiohttp.request(method='GET', url=url) as resp:
            content = await resp.text()
            content = json.loads(content)
            CheckESErrorException(resp.status, content)
            if resp.status >= 300:
                cause = "Service is not initialized."
                error_detail = {
                    "Error": content["error"],
                    "traceback": traceback.format_exc(),
                }
                raise InternalErrorException(cause=cause, detail=error_detail)
            
        if content["hits"]["hits"]:
            return content["hits"]["hits"][0]["_source"]["label"]
    except InternalErrorException:
        raise
    except Exception:
        cause = "Failed to connect to ElasticSearch."
        error_detail = {
            "error": "Invalid path of ElasticSearch.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)
            
    # Generate visual feature labels
    try:
        visual_labels = await GetVisualLabels(image)
        index_sequence = [x % INDEX_NUM for x in visual_labels['global'][0][:4]]
        index_sequence = set(index_sequence)
        vid_list = visual_labels['local'][:300]
        vid_list.sort()
    except:
        cause = "Failed to connect to DL-Inference-Serving."
        error_detail = {
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

    # Search by visual feature labels
    try:
        urls = [f'{ELASTICSEARCH_PATH}/delg_{x}/{INDEX_TYPE}/_search' \
            for x in index_sequence]
        match_condi = [{"match": {"vid": x}} for x in vid_list]
        data = {
            "_source": {
                "include": ["label"],
                "exclude": ["vid"],
            }, 
            "query" : {
                "bool": {
                    "should": match_condi,
                },
            },
            "size": 20,
        }
        query_label = []
        for url in urls:
            async with aiohttp.request(method='POST', url=url, json=data) \
                as resp:
                content = await resp.text()
                content = json.loads(content)
                CheckESErrorException(resp.status, content)
            query_label += [(x["_score"], x["_source"]["label"]) for x in \
                content["hits"]["hits"] if bool(x)]
        if len(query_label) >= 1:
            result_labels = sorted(query_label)
            result_labels = ScoreFilter(result_labels[-20:])
            return result_labels
        else:
            return query_label
    except:
        cause = "Failed to connect to ElasticSearch."
        error_detail = {
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)