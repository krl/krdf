# -*- encoding:utf-8 -*-

# from bsddb3 import db
# import cPickle as pickle

import couchdb

################################
# graph class

class Graph ():
  def __init__(self, address, db_name):
    server = couchdb.Server(address)
    if not server.__contains__(db_name):
      server.create(db_name)
    self.db = server[db_name]
    if not self.db.__contains__('_design/index'):
      self.db['_design/index'] = {"views": {
          "s"  : {"map": "function(doc) {emit(doc.s, doc);}"},
          "sp" : {"map": "function(doc) {emit([doc.s, doc.p], doc);}"},
          "spo": {"map": "function(doc) {emit([doc.s, doc.p, doc.o], doc);}"},
          "po" : {"map": "function(doc) {emit([doc.p, doc.o], doc);}"}}}

  def add(self, s, p, o, t):
    #print "add",s, p, o, t
    self.db.create({'s': s.decode('utf-8'),
                    'p': p.decode('utf-8'),
                    'o': o.decode('utf-8'),
                    't': t.decode('utf-8')})

  def remove(self, s=None, p=None, o=None):
    #print "remove", s,p,o
    for x in self.get(s,p,o):
      del self.db[x['_id']]

  def set(self, s, p, o, t):
    self.remove(s, p)
    self.add(s, p, o, t)

  def get(self, s=None, p=None, o=None):
    #print "get", s,p,o
    ret = []
    if s and p and o:
      return [x.value for x in self.db.view('_view/index/spo', None, key=[s, p, o])]

    elif s and not p and not o:
      return [x.value for x in self.db.view('_view/index/s', None, key=s)]

    elif s and p and not o:
      return [x.value for x in self.db.view('_view/index/sp', None, key=[s, p])]

    elif not s and p and o:
      return [x.value for x in self.db.view('_view/index/po', None, key=[p, o])]

    if not s and not p and not o:
      return [x.value for x in self.db.view('_view/index/spo')]

    else:
      raise Exception("combination not supported")
        
    return ret
