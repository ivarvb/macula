#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Ivar Vargas Belizario
# Copyright (c) 2020
# E-mail: ivar@usp.br


import sys

from vx.macula.Server import *

import tornado

if __name__ == "__main__":
    try:
        Server.execute()
    except KeyboardInterrupt:
        # signal.signal(signal.SIGINT, signal_handler)
        tornado.ioloop.IOLoop.instance().stop()


