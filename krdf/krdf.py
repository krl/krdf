# -*- encoding:utf-8 -*-

from tokyocabinet import table
from hashlib import sha1
import re, cjson

db = table.Table()
db.open('rdf.tct', table.TDBOWRITER | table.TDBOCREAT)

literal = "l"
uri = "u"
decimal = "d"

callbacks = []

def triplehash(sub, prd, obj):
  return sha1(sub + "\n" + prd + "\n" + obj).hexdigest()

class Namespace():
  def __init__(self, base):
    self.base = base    
  
  def __getattr__(self, attr):
    return self.base + attr;

  def __str__(self):
    return self.base

class Resource(object):
  def __init__(self, uri):
    self.schema = {}
    self.uri = uri
    # for this object to look and behave in a nice way we'll resort to
    # some black magic here.
    # first loop through the variables set in the (sub)class definition and
    # move them to the self.schema dictionary.
    # the original slots are replaced by the schemas default value
    for x in dir(self):
      attr = object.__getattribute__(self, x)
      if isinstance(attr, Single):
        attr.sub = self.uri
        self.schema[x] = attr
        object.__setattr__(self, x, attr.obj)

  def __getattribute__(self, name):
    schema = object.__getattribute__(self,'schema')
    if schema.has_key(name):
      return schema[name].get(self.uri)
    else:
      return object.__getattribute__(self,name)

  def __getitem__(self, key):
    q = db.query()
    q.addcond('sub', table.TDBQCSTREQ, self.uri)
    q.addcond('prd', table.TDBQCSTREQ, key)
    res = q.search()
    if len(res):
      return db[res[0]]['obj']

  def commit(self):
    for k, v in self.schema.iteritems():
      value = object.__getattribute__(self,k)
      if value:
        # only the values that actually changed or has a default will
        # be committed
        v.set(self.uri, value)
    for x in callbacks:
      res = Resource(self.uri)
      x(res)

  def tojson(self):
    vals = {}
    q = db.query()
    q.addcond('sub', table.TDBQCSTREQ, self.uri)
    res = q.search()
    for x in res:
      v = db[x]
      if v['objtype'] == uri:
        typ = "uri"
      else:
        typ = "literal"

      vals[v['prd']] = [{"value":v['obj'],
                      "type" :typ}]

    return cjson.encode({self.uri: vals})

  @classmethod
  def getsorted(self, sortby, **kwargs):
    result = set([])
    for x in dir(self):
      attr = getattr(self, x)
      if isinstance(attr, Single) and attr.obj:
        q = db.query()
        q.addcond('prd', table.TDBQCSTREQ, attr.prd)
        q.addcond('obj', table.TDBQCSTREQ, attr.obj)
        res = q.search()
        keys = [db[x]['sub'] for x in res]
        if result:
          result = result.intersection(keys)
        else:
          result = set(keys)
 
    for k,v in kwargs.iteritems():
      attr = getattr(self, k)
      if isinstance(attr, Single):
        q = db.query()
        q.addcond('prd', table.TDBQCSTREQ, attr.prd)
        q.addcond('obj', table.TDBQCSTREQ, v)
        res = q.search()
        keys = [db[x]['sub'] for x in res]
        if result:
          result = result.intersection(keys)
        else:
          result = set(keys)
 
    if sortby:
      order = []
      for r in result:
        q = db.query()
        q.addcond('sub', table.TDBQCSTREQ, r)
        q.addcond('prd', table.TDBQCSTREQ, sortby)
        res = q.search()
        order.append([long(db[res[0]]['obj']), r])
      order.sort()
      return [self(x[1]) for x in order]

    return [self(x) for x in result]

  @classmethod
  def get(self, **kwargs):
    return self.getsorted(None, **kwargs)

class Single(object):
  def __init__(self, prd, objtype=literal, default=None):
    self.prd = prd
    self.obj = default
    self.objtype = objtype
    self.id = ""

  def get(self, sub):
    q = db.query()
    q.addcond('sub', table.TDBQCSTREQ, sub)
    q.addcond('prd', table.TDBQCSTREQ, self.prd)
    res = q.search()
    if len(res):
      if self.objtype == literal:
        return db[res[0]]['obj'].decode('utf-8') # ENCODING CRAP
      elif self.objtype == uri:
        return Resource(db[res[0]]['obj'])
      else:
        return self.objtype(db[res[0]]['obj'])
    else:
      if self.objtype == literal:
        return ""
      else:
        return None

  def set(self, sub, obj):
    # remove (all, but should only be one) old.
    q = db.query()
    q.addcond('sub', table.TDBQCSTREQ, sub)
    q.addcond('prd', table.TDBQCSTREQ, self.prd)
    res = q.search()
    for k in res:
      db.out(k)

    # directly add uris from Resources
    if hasattr(obj, "uri"):
      obj = obj.uri

    self.id = triplehash(sub, self.prd, obj)
    db[self.id] = {'sub'    : sub, 
                   'prd'    : self.prd,
                   'obj'    : obj, 
                   'objtype': "u" if type(self.objtype) != str else self.objtype}

def makeuri(seed):
  "make uri from seed"
  uri = ""
  valid = re.compile("[a-zA-Z0-9:,/#-_.!~*'()]")
  count = 2
  for x in re.sub(" ", "-", seed):
    if valid.match(x):
      uri += x
  _try = uri

  while True:
    q = db.query()
    q.addcond('sub', table.TDBQCSTREQ, _try)    
    if not q.search():
      break
    _try = uri + "_" + str(count)
    count += 1
  return _try

def dumpdb():
  return [db[x] for x in db.query().search()]

def register_commit_callback(callback):
  callbacks.append(callback)
