#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ivar Vargas Belizario
# Copyright (c) 2022
# E-mail: ivar@usp.br

import os

    
class Settings:
    VERSION = 3.0
    DBACCESS = 0 # for MongoDB configuration without user and password
    #DBACCESS = 1 # for MongoDB configuration with user and password
    ROOTID = 0
    DEBUG = True
    MULIUSER = 1
    DIRNAME = os.path.dirname(__file__)
    IMPORT_PATH = os.path.join(DIRNAME, './import')
    #STATIC_PATH = os.path.join(DIRNAME, './static')
    #TEMPLATE_PATH = os.path.join(DIRNAME, './templates')
    DATA_PATH = os.path.join(DIRNAME, '../../../../data/macula/')

    COOKIE_SECRET = 'L8LwECidDfdhxq2W3434WrdfF62wfsRerx9MZlrpmu2DGgHvDmlydNX/vt1LM='

    HOST = 'localhost'
    PORT = 8222

    PATHROOT = "http://localhost:"+str(PORT)+"/"

class DBS:
    # Change USER_HERE, PASSWORD_HERE or DB_HERE
    DBMACULA = {
        "host":"127.0.0.1",
        "port":"27017",
        "username":"",#USER_HERE
        "password":"",#PASSWORD_HERE
        "database":"macula",#DB_HERE
        "audb":"admin"
    };
