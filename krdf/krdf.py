from pyrant import Tyrant
from hashlib import sha1
import re

t = Tyrant(host='127.0.0.1', port=1978)

literal = "l"
uri = "u"

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

  def commit(self):
    for k, v in self.schema.iteritems():
      value = object.__getattribute__(self,k)
      if value:
        # only the values that actually changed or has a default will
        # be committed
        v.set(self.uri, value)

  @classmethod
  def get(self, **args):
    result = set([])
    for x in dir(self):
      attr = getattr(self, x)
      if isinstance(attr, Single) and attr.obj:
        res = t.query.filter(prd=attr.prd)
        res = res.filter(obj=attr.obj)
        keys = [x.values()[0]['sub'] for x in res]
        if result:
          result = result.intersection(keys)
        else:
          result = set(keys)

    for k,v in args.iteritems():
      attr = getattr(self, k)
      if isinstance(attr, Single):
        res = t.query.filter(prd=attr.prd)
        res = res.filter(obj=v)
        keys = [x.values()[0]['sub'] for x in res]
        if result:
          result = result.intersection(keys)
        else:
          result = set(keys)

    return [self(x) for x in result]

class Single(object):
  def __init__(self, prd, obj=None, objtype=literal):
    self.prd = prd
    self.obj = obj
    self.objtype = objtype
    self.id = ""

  def get(self, sub):
    res = t.query.filter(sub=sub)
    res = res.filter(prd=self.prd)
    if len(res):
      if self.objtype == literal:
        return res[0].values()[0]['obj']
      elif self.objtype == uri:
        return Resource(res[0].values()[0]['obj'])
      else:
        return self.objtype(res[0].values()[0]['obj'])
    else:
      if self.objtype == literal:
        return ""
      else:
        return None

  def set(self, sub, obj):
    # remove (all, but should only be one) old.
    res = t.query.filter(sub=sub)
    res = res.filter(prd=self.prd)    
    for k in res:
      del t[k.keys()[0]]

    # directly add uris from Resources
    if hasattr(obj, "uri"):
      obj = obj.uri

    self.id = triplehash(sub, self.prd, obj)
    t[self.id] = {'sub': sub, 'prd'    : self.prd,
                  'obj': obj, 'objtype': self.objtype}

def makeuri(seed):
  "make uri from seed"
  uri = ""
  valid = re.compile("[a-zA-Z0-9:,/#-_.!~*'()]")
  count = 2
  for x in re.sub(" ", "-", seed):
    if valid.match(x):
      uri += x
  _try = uri

  while len(t.query.filter(sub=_try)):
    _try = uri + "_" + str(count)
    count += 1
  return _try

rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

def dumpdb(self):
  return [x.values()[0] for x in t.query.filter()]
