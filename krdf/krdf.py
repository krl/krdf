# -*- encoding:utf-8 -*-
from graph import Graph
import re, cjson, os

literal = "l"
uri = "u"
decimal = "d"

SELF = "self"

class Namespace():
  def __init__(self, base):
    self.base = base    
  
  def __getattr__(self, attr):
    return self.base + attr;

  def __str__(self):
    return self.base

class Database():
  def __init__(self, address, db_name):
    self.address = address
    self.db_name = db_name
    self.graph = Graph(address, db_name)
    self.callbacks = []
    
    reference = self

    class _Resource(object):
      _db     = reference # accessable to classmethods.

      # make an instance of this resource
      def __init__(self, uri):
        self._uri = uri
        self._values = {}

        # loop through the schema items set in (sub)class definition
        for k, v in self.__class__.__dict__.iteritems():
          if isinstance(v, Schema):
            if v.objtype == SELF:
              v.objtype = self.__class__

            if isinstance(v, Multiple):
              self._values[k] = MultipleDelta(self, v)

            # has default?
            if isinstance(v, Single) and v.default:
              self._values[k] = v.default

      def commit(self):
        for k, v in self.__class__.__dict__.iteritems():
          if self._values.has_key(k):
            self._get(k).set(self._values[k], self)

      def remove(self):
        self._db.graph.remove(self._uri)

      def __setattr__(self, key, value):        
        try:
          obj = object.__getattribute__(self, key)
          if isinstance(obj, Single):
            self._values[key] = value
          elif isinstance(obj, Multiple):
            raise Exception("Cannot assign values to Multiple")
          else:
            object.__setattr__(self, key, value)
        except AttributeError:
          object.__setattr__(self, key, value)

      def _get(self, key):
        # convenience getattr without API conciderations.
        return object.__getattribute__(self, key)

      def __getattribute__(self, key):
        try:
          obj = object.__getattribute__(self, key)
        except AttributeError:
          return None

        if isinstance(obj, Single):
          if obj.objtype == literal or obj.objtype == uri:
            return obj.read(self)
          else:
            return obj.objtype(obj)
        elif isinstance(obj, Multiple):
          return self._values[key]
        else: # standard object members
          return obj

      @classmethod
      def get(self, **kwargs):
        sets = []
        # which Resources fits in on all schema constraints?
        
        for k, v in self.__dict__.iteritems():
          # does this value has a default that should be matched?
          if isinstance(v, Single) and v.default:
            sets.append(set([x['s'] for x in self._db.graph.get(None, v.prd, v.default)]))
            
        for k,v in kwargs.iteritems():
          attr = getattr(self, k)
          sets.append(set([x['s'] for x in self._db.graph.get(None, attr.prd, v)]))
    
        if sets:      
          return [self(x) for x in sets[0].intersection(*sets[1:])]
        else:
          return []

    ## continuation of class Database __init__ here
    self.Resource = _Resource

  ## direct database methods

  def dump(self):
    return self.graph.get()

class Schema(object):
  pass

class Single(Schema):
  def __init__(self, prd, objtype=literal, default=None):
    self.prd     = prd
    self.objtype = objtype
    self.default = default

  def set(self, obj, parent):
    parent._db.graph.set(parent._uri, self.prd, str(obj), self.objtype)

  def read(self, parent):    
    return parent._db.graph.get(parent._uri, self.prd, None)[0]['o']

class MultipleDelta():
  def __init__(self, parent, schema):
    self.parent = parent
    self.schema = schema
    self.reset()

  def reset(self):
    self.addlist = []
    self.removelist = []

  def add(self,obj):
    self.addlist.append(obj)

  def remove(self,obj):
    self.removelist.append(obj)

  def get(self):
    result = self.parent._db.graph.get(self.parent._uri, self.schema.prd)
    return [self.schema.objtype(x['o']) for x in result]

class Multiple(Schema):
  def __init__(self, prd, objtype):
    self.prd     = prd
    self.objtype = objtype
    
  def set(self, delta, parent):
    for x in delta.addlist:
      parent._db.graph.add(parent._uri, self.prd, x._uri,
                           uri if self.objtype != literal else literal)
    for x in delta.removelist:
      parent._db.graph.remove(parent._uri, self.prd, x._uri)
    
  #delta.reset()
