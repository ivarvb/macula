#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ivar Vargas Belizario
# Copyright (c) 2020
# E-mail: ivar@usp.br

import tornado.ioloop
import tornado.web
import tornado.httpserver
import ujson
import bcrypt


from vx.com.py.database.MongoDB import *

from vx.macula.Settings import *
from vx.macula.User import *

class BaseHandler(tornado.web.RequestHandler):   
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get_current_user(self):
        if Settings.MULIUSER == 0:
            return "localuser"
        elif Settings.MULIUSER == 1:
            return self.get_secure_cookie("user")

    def get_current_email(self):
        return "localuser"
        """ if Settings.MULIUSER == 0:
            return "localuser"
        elif Settings.MULIUSER == 1:
            return self.get_secure_cookie("email") """

    def get_current_adminid(self):
        if Settings.MULIUSER == 0:
            return "localuser"
        elif Settings.MULIUSER == 1:
            return self.get_secure_cookie("adminid")
        # return self.get_secure_cookie("adminid")




class Login(BaseHandler):
    def get(self):
        if Settings.MULIUSER==1:
            self.render("login.html")
        else:
            self.redirect("./")
        return

    def post(self):
        op = int(self.get_argument('option'))

        re = User.login(    self.get_argument('user'),
                            self.get_argument('password') );
        if len(re)==1:
            for r in re:
                uid = str(r['_id'])
                #uid = ""+uid+"".decode("utf-8")
                self.set_secure_cookie("user", uid)
                self.set_secure_cookie("email", r['email'])
                #print("r['adminid']",r['adminid']);
                self.set_secure_cookie("adminid", str(r['adminid']))

                #self.set_secure_cookie("user", uid, expires_days=1)
                #self.set_secure_cookie("email", r['email'], expires_days=1)
            self.redirect("./")
            return
        else:
            self.redirect("./login")
            return

        return


class Logout(BaseHandler):
    def get(self):
        self.clear_cookie('user')
        self.clear_cookie('email')
        self.redirect("./")



class Index(BaseHandler):
    def get(self):
        """ 
        if not self.current_user:
            self.redirect("./login")
            return
        else:
            #print("self.get_current_email()", self.get_current_email())
            #self.render("index.html",email=self.get_current_email(), pathroot=Settings.PATHROOT)
            self.redirect("./Layout") """
        self.redirect("./layout")


class Layout(BaseHandler):
    def get(self):
        self.render("layout.html",email=self.get_current_email())
        """ if not self.current_user:
            self.redirect("./login")
            return
        else:
            self.render("layout.html",email=self.get_current_email())
        """
