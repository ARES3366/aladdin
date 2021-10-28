#!/usr/bin/env python
# -*- coding:utf-8 -*-
import tornado.web
#from read_config import *
from read_config import worker_processes,server_port
from .content_handler import PandoraBaseHandler

class ServerInfoHandler(tornado.web.RequestHandler):

    def get(self):
        info = {
            "status": 0,
            "server_status": "ok",
            "server_port": str(server_port),
            "multiprocess_num": worker_processes,
            "overstock_body_size": PandoraBaseHandler.overstock_body_len
        }
        self.write(info)
