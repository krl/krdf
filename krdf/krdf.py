# -*- encoding:utf-8 -*-
from graph import Graph
import re, cjson, os

graph = Graph("test")

literal = "l"
uri = "u"
decimal = "d"

callbacks = []

SELF = "self"

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
        if attr.objtype == SELF:
          attr.objtype = self.__class__
        # copy the class instance
        self.schema[x] = Single(attr.prd, attr.objtype, attr.obj)
        self.schema[x].sub = self.uri
        object.__setattr__(self, x, attr.obj)
      if isinstance(attr, Multiple):
        if attr.objtype == SELF:
          attr.objtype = self.__class__
        # copy the class instance
        self.schema[x] = Multiple(attr.prd, attr.objtype)
        self.schema[x].sub = self.uri
        object.__setattr__(self, x, attr)

  def __getattribute__(self, name):
    schema = object.__getattribute__(self,'schema')
    if schema.has_key(name):
      return schema[name].read()
    else:
      return object.__getattribute__(self,name)

  def __getitem__(self, key):
    res = graph.get(self.uri, key)
    if len(res):
      return db[res[0]]['o']

  def remove(self):
    graph.remove(self.uri)

  def commit(self):
    for k, v in self.schema.iteritems():
      value = object.__getattribute__(self,k)
      if value:
        # only the values that actually changed or has a default will
        # be committed
        v.set(value)
    callback(self.uri)

  def tojson(self):    
    return cjson.encode(self.todict())

  def todict(self):
    vals = {}    
    res = graph.get(self.uri)
    for x in res:
      if x['t'] == literal:
        typ = "literal"
      else:
        typ = "uri"

      vals[x['p']] = [{"value":x['o'],
                       "type" :typ}]

    return {self.uri: vals}

  def __str__(self):
    return self.uri

  @classmethod
  def getsorted(self, sortby, **kwargs):
    # this will need to be optimized sometime to add indexes for frequently
    # sorted arguments.
    return self.get(**kwargs)

  @classmethod
  def get(self, **kwargs):
    sets = []
    # which Resources fits in on all schema constraints?
    for x in dir(self):
      attr = getattr(self, x)
      # does this value has a default (attr.obj) that should be matched?
      if isinstance(attr, Single) and attr.obj:
        sets.append(set([x['s'] for x in graph.get(None, attr.prd, attr.obj)]))
        
    for k,v in kwargs.iteritems():
      attr = getattr(self, k)
      sets.append(set([x['s'] for x in graph.get(None, attr.prd, v)]))

    if sets:      
      return [self(x) for x in sets[0].intersection(*sets[1:])]
    else:
      return []

class Multiple(object):
  def __init__(self, prd, objtype=literal):
    self.prd = prd
    self.objtype = objtype
    self.sub = None
    self.addlist, self.removelist = [], []

  def add(self, obj):
    self.addlist.append(obj)

  def read(self):
    return self

  def get(self):
    res = graph.get(self.sub, self.prd)
    ret = []

    if len(res):
      for x in res:
        if self.objtype == literal:
          ret.append(x['o'].decode('utf-8')) # ENCODING CRAP
        elif self.objtype == uri:
          ret.append(Resource(x['o']))
        else:
          ret.append(self.objtype(x['o']))
    return ret

  def set(self, dummy):
    for obj in self.addlist:
      # directly add uris from Resources
      if hasattr(obj, "uri"):
        obj = obj.uri
      
      graph.set(self.sub, self.prd, obj, 
                uri if type(self.objtype) != str else self.objtype)

class Single(object):
  def __init__(self, prd, objtype=literal, default=None):
    self.prd = prd
    self.obj = default
    self.objtype = objtype
    self.id = ""
    self.sub = None

  def read(self):
    res = graph.get(self.sub, self.prd)
    if len(res):
      if self.objtype == literal:
        return res[0]['o']
      elif self.objtype == uri:
        return Resource(res[0]['o'])
      else:
        return self.objtype(res[0]['o'])
    else:
      if self.objtype == literal:
        return ""
      else:
        return None

  def set(self, obj):
    # directly add uris from Resources

    if hasattr(obj, "uri"):
      obj = obj.uri

    graph.set(self.sub, self.prd, obj,
              uri if type(self.objtype) != str else self.objtype)

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
    if not graph.get(_try):
      break
    _try = uri + "_" + str(count)
    count += 1
  return _try

def dumpdb():
  ret = []

  for x in graph.get():
    x['o'] = x['o']
    ret.append(x)
  return ret

def callback(uri):
  for x in callbacks:
    res = Resource(uri)
    x(res)

def register_commit_callback(callback):
  callbacks.append(callback)

def tojson(*args):
  "converts x resources into a json rdf representation"
  dict = {}
  for x in args:
    dict.update(x.todict())

  return cjson.encode(dict)

def fromdict(dictionary):
  for k, v in dictionary.iteritems():
    for kk, vv in v.iteritems():
      for x in vv:
        # using first character of type only. ("l", "u")
        s = Single(kk, x['type'][0])
        s.set(k, x['value'])
    callback(k)

def fromjson(jsonstring):
  fromdict(cjson.decode(jsonstring))
