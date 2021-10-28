#!/usr/bin/env python
# -*- coding:utf-8 -*-
import multiprocessing
multiprocessing.set_start_method('forkserver', force=True)
multiprocessing.freeze_support()
import logging
import asyncio
import tornado
import tornado.web
import tornado.ioloop
import tornado.httpserver
from tornado.options import define, options
from read_config import *
from handler.server_handler import ServerInfoHandler
define("port", default=server_port, help="run on the given port", type=int)

import sys
# logging.StreamHandler(stream=sys.stdout)
# logging.basicConfig(stream=sys.stdout)

log_level = logging.WARNING
if 'LOG_LEVEL' in os.environ:
    slevel = os.environ['LOG_LEVEL']
    print(slevel)
    if slevel == 'NOTSET':
        log_level=logging.NOTSET
    if slevel == 'DEBUG':
        log_level=logging.DEBUG
    if slevel == 'INFO':
        log_level=logging.INFO
    if slevel == 'WARNING':
        log_level=logging.WARNING
    if slevel == 'ERROR':
        log_level=logging.ERROR
    if slevel == 'CRITICAL':
        log_level=logging.CRITICAL
# logging.basicConfig(level=log_level, format="%(process)s\t%(asctime)s\t%(levelname)s\t%(message)s")
logging.basicConfig(stream=sys.stdout,level=log_level, format="[%(levelname)s]\t%(asctime)s|%(process)s[%(threadName)s]|%(thread)d\t%(filename)s(%(pathname)s)[line:%(lineno)d] %(funcName)s\t%(message)s")

class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/health/ready", MainHandler),
            (r"/health/alive", MainHandler),
            (r"/server/infos", ServerInfoHandler),
        ]
        if service_type in ['all', 'fast-text-analysis']:
            from handler.content_handler import BatchSensitivityHandler
            from handler.content_handler import IllegalityHandler
            from handler.content_handler import PrivacyRecognizeHandler
            from handler.content_handler import PrivacyProperytHandler
            from handler.content_handler import ExtractDocFingerPrintClusterHandler
            from handler.content_handler import ExtractFingerPrintKeywordsHandler  
            from handler.fta_handler import FtaHandler,FtaKeywordsHandler
            handlers += [
                (r"/api/fast-text-analysis/v1/matchwords", BatchSensitivityHandler),
                (r"/api/fast-text-analysis/v1/illegality", IllegalityHandler),
                (r"/api/fast-text-analysis/v1/privacy-recognition", PrivacyRecognizeHandler),
                (r"/api/fast-text-analysis/v1/privacy-properties", PrivacyProperytHandler),
                (r"/api/fast-text-analysis/v1/doc-fingerprint-cluster",ExtractDocFingerPrintClusterHandler), 
                (r"/api/fast-text-analysis/v1/analysis",FtaHandler), 
                (r"/api/fast-text-analysis/v1/fingerprint_keywords",FtaKeywordsHandler),   
            ]

        if service_type in ["all", "object-detection"]:
            from handler.object_detection_handler import SubMetaInfoHandler
            from handler.object_detection_handler import SubMetaInfoHandlerVid
            from handler.object_detection_handler import SubMetaInfoHandlerUrl
            # from handler.object_detection_handler import SubMetaInfoHandlerCid
            from handler.object_detection_handler import SearchHandler
            handlers += [
                (r"/api/object-detection/v1/sub-meta-info", SubMetaInfoHandler),
                (r"/api/object-detection/v1/sub-meta-info/url/(.+)", SubMetaInfoHandlerUrl),
                (r"/api/object-detection/v1/sub-meta-info/(.+)", SubMetaInfoHandlerVid),
                
                # (r"/api/object-detection/v1/sub-meta-info/cid/(.+)", SubMetaInfoHandlerCid),
                (r"/api/object-detection/v1/search", SearchHandler)
            ]
        if service_type in ['all', 'auto-text-filter']:
            from handler.atf_handler import ATFWordHandler
            from handler.atf_handler import ATFGroupHandler
            from handler.atf_handler import ATFConditionHandler
            from handler.atf_handler import ATFFilterHandler
            from handler.atf_handler import ATFFilterAnalysisHandler
            from handler.atf_handler import ATFAssignConditonHandler
            from handler.atf_handler import ATFMultiFilterHandler
            from handler.atf_handler import ATFMultiAnalysisHandler
            handlers += [
                (r"/api/auto-text-filter/v1/word", ATFWordHandler),
                (r"/api/auto-text-filter/v1/group",ATFGroupHandler),
                (r"/api/auto-text-filter/v1/condition",ATFConditionHandler),
                (r"/api/auto-text-filter/v1/assign_condition",ATFAssignConditonHandler),
                (r"/api/auto-text-filter/v1/text_filter",ATFFilterHandler),
                (r"/api/auto-text-filter/v1/filter_analysis",ATFFilterAnalysisHandler),
                (r"/api/auto-text-filter/v1/multi_filter",ATFMultiFilterHandler),
                (r"/api/auto-text-filter/v1/multi_analysis",ATFMultiAnalysisHandler),
            ]

        if service_type in ['all', 'match-image']:
            from handler.match_image_handler import MatchImageIndexHandler
            from handler.match_image_handler import MatchImageSearchHandler
            handlers += [
                (r"/api/match-image/v1/index", MatchImageIndexHandler),
                (r"/api/match-image/v1/search", MatchImageSearchHandler),
            ]

        debug=False
        if ('DEBUG' in os.environ) and (os.environ['DEBUG'] == 'true'):
            debug = True
        settings = dict(
            debug=debug
        )

        tornado.web.Application.__init__(self, handlers, **settings)
        self.logger = logging.getLogger("pandora")


class MainHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        self.write("hello  world")


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application(),max_buffer_size=max_buffer_size, max_body_size=max_body_size)

    # tornado 多进程启动是使用os.fork实现,而windows中没有os.fork方法，
    # 因此在这里进行判断操作系统类型, 然后实现不同类型的tornado启动方式
    import platform
    sysstr = platform.system()
    if sysstr == "Windows":
        http_server.listen(options.port)
    else:
        #http_server.listen(9528)
        http_server.bind(server_port)
        # 0表示有几个cpu，就开启几个子进程
        http_server.start(worker_processes)
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
