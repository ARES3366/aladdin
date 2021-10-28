#!/usr/bin/env python
# -*- coding:utf-8 -*-
import traceback
import json
import tornado.web
import logging
from exception_handler import BasicException, InternalErrorException
from match_image.do_handler import MatchImageIndexPost
from match_image.do_handler import MatchImageIndexDelete
from match_image.do_handler import MatchImageSearchPost


class MatchImageIndexHandler(tornado.web.RequestHandler):
    """
    docstring
    """
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            response = await MatchImageIndexPost(params)
            return self.write(json.dumps(response, ensure_ascii=False))
        except BasicException as err:
            self.set_status(err.status_code)
            self.write(err.generate_response())
        except BaseException:
            cause = "Unkown error."
            error_detail = {
                "traceback": traceback.format_exc(),
            }
            exception = InternalErrorException(cause=cause, detail=error_detail)
            self.set_status(500)
            self.write(exception.generate_response())

    async def delete(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            response = await MatchImageIndexDelete(params)
            return self.write(json.dumps(response, ensure_ascii=False))
        except BasicException as err:
            self.set_status(err.status_code)
            self.write(err.generate_response())
        except BaseException:
            cause = "Unkown error."
            error_detail = {
                "traceback": traceback.format_exc(),
            }
            exception = InternalErrorException(cause=cause, detail=error_detail)
            self.set_status(500)
            self.write(exception.generate_response())


class MatchImageSearchHandler(tornado.web.RequestHandler):
    """
    docstring
    """
    async def post(self, *args, **kwargs):
        try:
            params = json.loads(self.request.body.decode())
            response = await MatchImageSearchPost(params)
            return self.write(json.dumps(response, ensure_ascii=False))
        except BasicException as err:
            self.set_status(err.status_code)
            self.write(err.generate_response())
        except BaseException:
            cause = "Unkown error."
            error_detail = {
                "traceback": traceback.format_exc(),
            }
            exception = InternalErrorException(cause=cause, detail=error_detail)
            self.set_status(500)
            self.write(exception.generate_response())