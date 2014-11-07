# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 12:45:01 2014

@author: Matt
"""

import web
import sql
import sqlite3
from sql import index #just in case

web.config.debug = False

if __name__ == "__main__":
    app = web.application(sql.urls, globals())
    app.run()