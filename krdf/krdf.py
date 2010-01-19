# -*- encoding:utf-8 -*-
import re, cjson, os
import couchdb

import types
import views
from resource import *

class Namespace():
  def __init__(self, base):
    self.base = base    
  
  def __getattr__(self, attr):
    return self.base + attr;

  def __str__(self):
    return self.base

class Database():
  def __init__(self, address, db_name, overwrite=False):
    self.cache = {}
    self.callbacks = []
    self.server = couchdb.Server(address)
    
    try:
      self.db = self.server.create(db_name)
    except:
      if overwrite:
        del self.server[db_name]
        self.db = self.server.create(db_name)
      else:
        self.db = self.server[db_name]

    # if self.server.__contains__(db_name) and overwrite:
    #   del self.server[db_name]

    # if not self.server.__contains__(db_name):
    #   self.server.create(db_name)

    # self.db = self.server[db_name]    

    ## setup views

    if not self.db.__contains__('_design/index'):
      self.db['_design/index'] = views.index

    reference = self

    # resource subclassing
    class _Resource(Resource):      
      _ref = reference

    self.Resource = _Resource

  def register_save_callback(self, callback):
    self.callbacks.append(callback)

  def trigger_callback(self, uri):
    for x in self.callbacks:
      x(uri)

  def exists(self, uri):
    if not self.cache.has_key(uri):
      return self.db.__contains__(uri)
    else:
      return True

  def save(self, uri):
    self.db[uri] = self.cache[uri]
          
  def clear_cache(self):
    self.cache = {}

  def get_doc(self, uri):
    if not uri:
      raise Exception("get_doc non-true uri")

    if not self.cache.has_key(uri):
      try:
        self.cache[uri] = dict(self.db[uri])
      except couchdb.client.ResourceNotFound:
        # initialize
        self.cache[uri] = {"type": "resource", "data":{}}

    return self.cache[uri]

  def sortview(self, prd):
    view_id = str(hash(prd))

    # if not already created
    if not self.db.__contains__("_design/"+view_id):
      self.db["_design/"+view_id] = {"views": {"view": {"map" : views.sorting % prd}}}

    view_path = view_id + "/view"

    return view_path

  def makeuri(self, seed):
    "make uri from seed"
    uri = ""
    valid = re.compile("[a-zA-Z0-9:,/#-_.!~*'()]")
    count = 2
    for x in re.sub(" ", "-", seed):
      if valid.match(x):
        uri += x
    _try = uri
 
    while True:
      if not self.exists(_try):
        break
      _try = uri + "_" + str(count)
      count += 1
    return _try

  def tojson(self, *uris):
    return cjson.encode(dict([[y._uri, self.get_doc(y._uri)['data']] for y in uris]))
