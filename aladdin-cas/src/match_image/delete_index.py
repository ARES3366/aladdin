import asyncio
import aiohttp
import traceback
import json
import numpy as np
from match_image.utils import *
from exception_handler import InternalErrorException


async def RemoveImageLabels(labels):
    # Search labels from Elasticsearch
    try:
        url = f'{ELASTICSEARCH_PATH}/{ALIASES}/_search'
        match_condi = [{"match": {"label": x}} for x in labels]
        data = {
            "version": "true",
            "_source": {
                "include": ["label", ],
                "exclude": ["vid", ],
            }, 
            "query" : {
                "bool": {
                    "should": match_condi
                },
            },
            "size": 1000,
        }
        async with aiohttp.request(method='POST', url=url, json=data) as resp:
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
    except:
        cause = "Failed to connect to ElasticSearch."
        error_detail = {
            "error": "Invalid path of ElasticSearch.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)
    # Remove labels from Elasticsearch
    try:
        result = []
        error_result = []
        info = content["hits"]["hits"]
        for x in info:
            original_label = x['_source']['label']
            new_label = [i for i in original_label if i not in labels]
            if bool(new_label):
                update_data = {
                    "doc": {
                        "label": new_label,
                    }
                }
                url = "{path}/{index}/{type}/{id}/{op}?version={ver}".format(
                    path=ELASTICSEARCH_PATH,
                    index=x["_index"],
                    type=x["_type"],
                    id=x["_id"],
                    op="_update",
                    ver=x["_version"],
                )
                async with aiohttp.request(method='POST', url=url, json=update_data) as resp:
                    if resp.status == 409:
                        result.append(False)
                        error_result += [i for i in labels if i in original_label]
                    elif resp.status <= 201:
                        result.append(True)
                    elif resp.status == 404:
                        result.append(False)
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
                url = "{path}/{index}/{type}/{id}?version={ver}".format(
                    path=ELASTICSEARCH_PATH,
                    index=x["_index"],
                    type=x["_type"],
                    id=x["_id"],
                    ver=x["_version"],
                )
                async with aiohttp.request(method='delete', url=url) as resp:
                    if resp.status == 409:
                        result.append(False)
                    elif resp.status <= 201:
                        result.append(True)
                    elif resp.status == 404:
                        result.append(True)
                    else:
                        content = await resp.text()
                        content = json.loads(content)
                        CheckESErrorException(resp.status, content)
                        cause = "Internal error."
                        error_detail = {
                            "Error": content["error"],
                            "traceback": traceback.format_exc(),
                        }
                        raise InternalErrorException(cause=cause, detail=error_detail)
        if False in result:
            error_result = set(error_result)
            error_result = list(error_result)
            return False, error_result
        else:
            return True, error_result
    except InternalErrorException:
        raise
    except:
        cause = "Failed to connect to ElasticSearch."
        error_detail = {
            "error": "Invalid path of ElasticSearch.",
            "traceback": traceback.format_exc(),
        }
        raise InternalErrorException(cause=cause, detail=error_detail)