#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ivar Vargas Belizario
# Copyright (c) 2021
# E-mail: ivar@usp.br


import tornado.ioloop
import tornado.web
import tornado.httpserver

import ujson
import glob
import os
import time
import sys

import pandas as pd
import numpy as np
import os.path
import math
import uuid

import zipfile
from io import BytesIO
from datetime import datetime
import threading
#import SimpleITK as sitk
from bson.objectid import ObjectId


from vx.com.py.database.MongoDB import *


from vx.macula.Settings import *
from vx.macula.Pages import *

from vx.macula.Segmentation import *

class Query(BaseHandler):

    #Get RequestHandler
    def get(self):
        dat = self.get_argument('data')
        app = ujson.loads(dat)

        obj = ""

        if app["argms"]["type"]==0:
            pass;
        elif app["argms"]["type"]==1:
            obj = self.openproject();
        elif app["argms"]["type"]==2:
            obj = self.executeclassification(app["argms"]);
        elif app["argms"]["type"]==3:
            obj = self.semiautomatic(app["argms"]);
        self.write(obj)
        self.finish()


    #Post RequestHandler
    def post(self):
        dat = self.get_argument('data')
        app = ujson.loads(dat)
        rs = ""
        if self.current_user:
            #print("app.argms", app, self.request.files['fileu'][0])
            if app["argms"]["type"]==6:
                rs = Query.uploadfiledata(self.current_user, self.request.files['fileu'][0]);

        self.write(rs)

    @staticmethod
    def readFile(pathf):
        dfile = {}
        with open(pathf,'r') as fp:
            dfile = ujson.load(fp)
        return dfile

    @staticmethod    
    def writeFile(pathf, rdata):
        with open(pathf,'w') as fp:
            ujson.dump(rdata, fp)

    @staticmethod
    def openproject():
        fileso = []
        """
        for name in os.listdir(Settings.DATA_PATH):
            if name.endswith(".png") or name.endswith(".jpg") or name.endswith(".jpeg"):
                fileso.append({"name":str(name)})
        """

        ini = 2021
        months = ["01","02","03","04","05","06","07","08","09","10","11","12"]
        now = 2021
        for y in range(ini,now+1):
            for m in months:
                folder = os.path.join(Settings.DATA_PATH,str(y),str(m))
                if os.path.exists(folder):
                    for ide in os.listdir(folder):
                        if os.path.isdir(os.path.join(folder, ide)):
                            fileobj = os.path.join(folder, ide, "db.obj")
                            if os.path.exists(fileobj):
                                dat = Query.readFile(fileobj)
                                fileso.append(dat)
        fileso = sorted(fileso, key = lambda i: (i['date']), reverse=True)
        
        return {"response":fileso, "error":0}

    @staticmethod
    def makeclassification(usid, argms):
        idus = usid
        idpj = argms["idpj"]
        idrois = argms["idroi"]
        idmodelversion = argms["idmodelversion"]
        idmodel = argms["idmodel"]
        
        print("argms classs", argms)
        parthquery = os.path.join(Settings.DATA_PATH, argms["path"])
        #parthquery = os.path.join(Settings.DATA_PATH, argms["path"])
        ypred, labels = Classification.predict(parthquery, idmodelversion, idmodel, idrois)
        
        rs = {"yp":ypred, "labels":labels}
        print("rs", rs)

        return {"statusopt":0, "statusval":"", "response":rs}
        #return {"statusopt":0, "statusval":"", "response":[]}


    @staticmethod
    def semiautomatic(argms):
        cx = argms["cx"]
        cy = argms["cy"]

        print("argms semi", argms)
        rs = Segmentation.semi(cx, cy)
        print("rs", rs)
        return {"response":rs, "error":0}


    @staticmethod
    def now():
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def converid(idin):
        """ 
        #idin = file
        if Settings.MULIUSER == 1:
            #idin = idin.decode("utf-8");
            idin = ObjectId(idin) """
        idin = ObjectId(idin)
        return idin
