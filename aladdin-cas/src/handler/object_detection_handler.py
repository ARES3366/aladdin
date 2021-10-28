# -*- coding:utf-8 -*-

from base64 import encode
import json
from os import pathconf_names
from exception_handler import BasicException
import tornado.web
import traceback
from object_detection.image_search_handler import image_meta_data_post, image_meta_data_get, image_meta_data_delete, image_meta_data_put, similar_image_search_post
from exception_handler import ParamsException, InternalErrorException, MissingParamsException, ParamsWrongTypeException, InvalidParamsException
import numpy as np

# 通过vid删除的handler
class SubMetaInfoHandlerVid(tornado.web.RequestHandler):
    async def delete(self, *args, **kwargs):
        try:
            path_params = self.path_args[0].strip()
            if len(path_params) == 0:
                cause = "path parameter required"
                error_detail = {
                    "parameters":["vid"]
                }
                exception = ParamsException(cause=cause, detail = error_detail, error_code="000")
                self.set_status(int(exception.status_code))
                return self.write(exception.generate_response())
            vid_list = [vid.strip() for vid in path_params.split(",")]
            return_result = await image_meta_data_delete(vid_list, "vid")
        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())
        except Exception as err:
            
            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())

# 通过url删除的handler
class SubMetaInfoHandlerUrl(tornado.web.RequestHandler):
    
    async def delete(self, *args, **kwargs):
        try:
            path_params = self.path_args[0].strip()
            if len(path_params) == 0:
                cause = "path parameter required"
                error_detail = {
                    "parameters":["url"]
                }
                exception = ParamsException(cause=cause, detail = error_detail, error_code="000")
                self.set_status(int(exception.status_code))
                return self.write(exception.generate_response())
            url_list = [url.strip() for url in path_params.split(",")]
            return_result = await image_meta_data_delete(url_list, "url")
            print(url_list)

        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())
        except Exception as err:
            
            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())


# 通过CID删除的handler
class SubMetaInfoHandlerCid(tornado.web.RequestHandler):
    async def delete(self, *args, **kwargs):
        try:
            path_params = self.path_args[0].strip()
            if len(path_params) == 0:
                cause = "path parameter required"
                error_detail = {
                    "parameters":["cid"]
                }
                exception = ParamsException(cause=cause, detail = error_detail, error_code="000")
                self.set_status(int(exception.status_code))
                return self.write(exception.generate_response())
            cid_list = [cid.strip() for cid in path_params.split(",")]
            print(url_list)
            
        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())
        except Exception as err:
            
            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())

# sub-meta-info 元数据处理的handler
class SubMetaInfoHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            return_result = await image_meta_data_post(params)
        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())
        except Exception as err:

            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())

    async def get(self, *args, **kwargs):
        try:
            query_params = self.request.arguments
            params = dict(zip(list(query_params.keys()), [value[0].decode() for value in list(query_params.values())]))
            return_result = await image_meta_data_get(params)
            del return_result["code"]
            del return_result["message"]
            return self.write(return_result)
        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())
        except Exception as err:
            
            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())

        

    async def put(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            return_result = await image_meta_data_put(params)
            return return_result
        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())     
        except Exception as err:
            
            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())

# 搜索的handler
class SearchHandler(tornado.web.RequestHandler):
    async def post(self, *args, **kwargs):
        try:
            query_params = self.request.arguments
            query_params_dict = dict(zip(list(query_params.keys()), [value[0].decode() for value in list(query_params.values())]))
            try:
                body_params = json.loads(self.request.body.decode())
            except Exception as e:
                raise MissingParamsException(detail=dict(parameters=["url", "image", "url"]))
            return_result = await similar_image_search_post(query_params_dict, body_params)
            return self.write(return_result)
        except BasicException as err:
            status_code = int(err.status_code)
            self.set_status(status_code)
            return self.write(err.generate_response())
        except Exception as err:
            cause = "parameter processing exception"
            error_detail = {
                "traceback":traceback.format_exc(),
                "error": repr(err)
            }
            return_err = InternalErrorException(cause=cause, detail=error_detail, error_code="000")
            self.set_status(int(return_err.status_code))
            return self.write(return_err.generate_response())

