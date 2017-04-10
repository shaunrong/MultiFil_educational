#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals

import abc
import pymongo
import yaml

__author__ = 'Ziqin (Shaun) Rong'
__maintainer__ = 'Ziqin (Shaun) Rong'
__email__ = 'rongzq08@gmail.com'

"""
This module define DB connection singleton instance in the system
"""


class DBAccess(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, host, port, db, user, passwd):
        self._host = host
        self._port = port
        self._db = db
        self._user = user
        self._passwd = passwd
        self._connected_db = None
        self._connected = False
        self._client = None

    def connect(self):
        if not self._connected:
            self._client = pymongo.MongoClient(self._host, self._port)
            self._connected_db = self._client[self._db]
            self._connected_db.authenticate(self._user, self._passwd)
            self._connected = True

    def collection(self, collection):
        if self._connected_db is None:
            raise RuntimeError("The database haven't been connected.")
        return self._connected_db[collection]

    def close(self):
        self._client.close()
        self._connected = False

    @classmethod
    @abc.abstractmethod
    def db_access(cls):
        raise NotImplementedError


class MyDB(DBAccess):
    _instance = None

    @classmethod
    def db_access(cls):
        if cls._instance is None:
            with open("db_config.yaml", "r") as yf:
                confidential = yaml.load(yf)
                host = confidential['MyDB']['host']
                port = confidential['MyDB']['port']
                user = confidential['MyDB']['user']
                db = confidential['MyDB']['db_scripts']
                passwd = confidential['MyDB']['passwd']
                cls._instance = MyDB(host=host, port=port, user=user, db=db, passwd=passwd)
        return cls._instance


class MPDB(DBAccess):
    _instance = None

    @classmethod
    def db_access(cls):
        if cls._instance is None:
            with open("db_config.yaml", "r") as yf:
                confidential = yaml.load(yf)
                host = confidential['MPDB']['host']
                port = confidential['MPDB']['port']
                user = confidential['MPDB']['user']
                db = confidential['MPDB']['db_scripts']
                passwd = confidential['MPDB']['passwd']
                cls._instance = MyDB(host=host, port=port, user=user, db=db, passwd=passwd)
        return cls._instance
