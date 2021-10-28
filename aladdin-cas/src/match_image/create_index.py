import asyncio
import aiohttp
import traceback
import json
import numpy as np
from exception_handler import InternalErrorException
from match_image.utils import *
from match_image.extractor import FeatureExtractor


GetVisualLabels = FeatureExtractor(MODEL_CONFIG)

async def AddImageLabel(image, label):
    # Generate hash's value by gray image
    try:
        hash_value = AverageHash(image, 64)
    except:
        cause = "Picture format error."
        error_detail = {
            "error": "Failed to convert image to hash code.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

    # Search image's index by hash's value 
    try:
        url = "{0}/{1}/_search?version=true&&q=_id:{2}".format(
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
    except InternalErrorException:
        raise
    except Exception:
        cause = "Failed to connect to ElasticSearch."
        error_detail = {
            "error": "Invalid path of ElasticSearch.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

    # Add image's label in elasticsearch
    try:
        if content["hits"]["hits"]:
            info = content["hits"]["hits"][0]
            _index = info["_index"]
            _type = info["_type"]
            _version = info["_version"]
            original_label = info["_source"]["label"]

            if not isinstance(original_label, list):
                original_label = []

            if label in original_label:
                return True

            original_label.append(label)
            url = "{0}/{1}/{2}/{3}/_update?version={4}".format(
                ELASTICSEARCH_PATH,
                _index,
                _type,
                hash_value,
                _version,
            )
            data = {
                "doc": {
                    "label": original_label
                }
            }
            async with aiohttp.request(method='POST', url=url, json=data) as resp:
                if resp.status == 409:
                    return False
                if resp.status == 404:
                    return False
                elif resp.status <= 201:
                    return True
                else:
                    content = await resp.text()
                    content = json.loads(content)
                    CheckESErrorException(resp.status, content)
                    cause = "Internal Error."
                    error_detail = {
                        "Error": content["error"],
                        "traceback": traceback.format_exc(),
                    }
                    raise InternalErrorException(cause=cause, detail=error_detail)
        else:
            _type = 0
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
        _index = f"delg_{visual_labels['global'][0][0] % INDEX_NUM}"
        vid_list = visual_labels['local'][:300]
        vid_list.sort()
    except Exception:
        cause = "Failed to connect to DL-Inference-Serving."
        error_detail = {
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)

    # Create image's label in elasticsearch
    try:
        url = "{path}/{index}/{type}/{_id}/_create".format(
            path=ELASTICSEARCH_PATH,
            index=_index,
            type=INDEX_TYPE,
            _id=hash_value,
        )
        data = {
            "label": [label, ], 
            "vid": vid_list,
        }
        async with aiohttp.request(method='PUT', url=url, json=data) as resp:
            content = await resp.text()
            content = json.loads(content)
            CheckESErrorException(resp.status, content)
            if resp.status == 409:
                return False
            elif resp.status == 404:
                return False
            elif resp.status <= 201:
                return True
            else:
                cause = "Internal Error."
                error_detail = {
                    "error": content["error"],
                    "traceback": traceback.format_exc(),
                }
                raise InternalErrorException(cause=cause, detail=error_detail)
    except InternalErrorException:
        raise
    except Exception:
        cause = "Failed to connect to ElasticSearch."
        error_detail = {
            "error": "Invalid path of ElasticSearch.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)
