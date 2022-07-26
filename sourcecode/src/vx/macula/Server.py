#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ivar Vargas Belizario
# Copyright (c) 2020
# E-mail: ivar@usp.br

import tornado.ioloop
import tornado.web
import tornado.httpserver
import tornado.options
import tornado
import signal

import ujson
import datetime
from multiprocessing import cpu_count


import os
import signal
import subprocess

#from psutil import process_iter
#from signal import SIGTERM # or SIGKILL

#from ipy.dataio import *
#from ipy.db import *

from vx.com.py.database.MongoDB import *


from vx.macula.Settings import *
#from vx.uncertainty.BaseHandler import *
from vx.macula.Query import *
from vx.macula.Pages import *
#from vx.uncertainty.User import *

MongoDB.DBACCESS = Settings.DBACCESS

def sig_exit():
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(do_stop)

def do_stop():
    tornado.ioloop.IOLoop.instance().stop()


class Server(tornado.web.Application):
    """ is_closing = False """

    def __init__(self):
        handlers = [
            (r"/", Index),
            #(r"/login", Login),
            #(r"/logout", Logout),
            (r"/query", Query),
            (r"/layout", Layout),
            # page for each project
            #(r"/lung/(.*)", LungPage),
            #(r"/simil", Simil),
            (r"/lib/(.*)",tornado.web.StaticFileHandler, {"path": Settings.IMPORT_PATH+"/static/lib"},),
            (r"/img/(.*)",tornado.web.StaticFileHandler, {"path": Settings.IMPORT_PATH+"/static/img"},),
            (r"/data/(.*)",tornado.web.StaticFileHandler, {"path": Settings.DATA_PATH},),
            # (r"/data/(.*)",tornado.web.StaticFileHandler, {"path": "./static/data"},),
            # (r"/img/(.*)",tornado.web.StaticFileHandler, {"path": "./static/img"},)
        ]
        settings = {
            "template_path":os.path.join(Settings.IMPORT_PATH, "templates"),
            "static_path":os.path.join(Settings.IMPORT_PATH, "static"),
#            "debug":Settings.DEBUG,
            "cookie_secret": Settings.COOKIE_SECRET,
        }
        tornado.web.Application.__init__(self, handlers, **settings)

    @staticmethod
    def execute():

        #User.rootinit();

        print ('The server is ready: http://'+Settings.HOST+':'+str(Settings.PORT)+'/')
        server = tornado.httpserver.HTTPServer(Server())
        server.bind(Settings.PORT)
        server.start(cpu_count())
    #    tornado.ioloop.IOLoop.current().start()
    #    tornado.ioloop.IOLoop.instance().start()

        try:
            """ tornado.ioloop.PeriodicCallback(serverapp.try_exit, 100).start() """
            signal.signal(signal.SIGINT, sig_exit)
            tornado.ioloop.IOLoop.instance().start()

        # signal : CTRL + BREAK on windows or CTRL + C on linux
        except KeyboardInterrupt:
            print("Keyboard interrupt")
        finally:
            print("Server closed")


if __name__ == "__main__":
    try:
        Server.execute()
    except KeyboardInterrupt:
        # signal.signal(signal.SIGINT, signal_handler)
        tornado.ioloop.IOLoop.instance().stop()



""" from importlib.metadata import version

bibs = [
            "wheel",
            "numpy",
            "tornado",
            "ujson",
            "matplotlib",
            "pandas",
            "cython",
            "python-javabridge",
            "python-bioformats",
            "opencv-python",
            "psutil",
            "pipeproxy",
            "bcrypt",
            "bson",
            "pymongo",
            "SimpleITK",
            "scipy",
            "shapely", 
            "itk",
            "pyradiomics",
            "opencv-python",
            "scikit-image",
            "sklearn",
            "xgboost",
            "joblib",
            "javabridge"
        ]
for bi in bibs:
    print(bi,"==",version(bi))
 """