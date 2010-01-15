# -*- encoding:utf-8 -*-
import couchdb
import types
import re, cjson, os

class ObjType():
  pass

LITERAL = "literal"
URI = "uri"
NUMBER = "number"

SELF = "self"

class Namespace():
  def __init__(self, base):
    self.base = base    
  
  def __getattr__(self, attr):
    return self.base + attr;

  def __str__(self):
    return self.base

class Database():
  def __init__(self, address, db_name, overwrite=False):
    self.sortviewcache = {}
    server = couchdb.Server(address)

    if server[db_name]:
      if overwrite:
        del server[db_name]
        server.create(db_name)
    else:
      server.create(db_name)

    self._db = server[db_name]

    if not self._db.__contains__('_design/index'):
      self._db['_design/index'] = {"views": {
          "po" : {"map": """
function(doc) {
  for(x in doc.data) { 
    for(y in doc.data[x]) {
      emit([x, doc.data[x][y]['value']], doc);
    }
  }
}"""}}}

    self.callbacks = []
    reference = self

    class _Resource(object):
      # accessable to classmethods.
      _db       = reference._db

      # make an instance of this resource
      def __init__(self, uri, doc = None):
        self._callback = reference.callback
        self._uri = uri
        self._doc = doc

        if not doc:
          try:
            self._doc = self._db[uri]
          except:
            self._doc = {"type": "resource", "data":{}}

        # loop through the schema items set in (sub)class definition
        for k, v in self.__class__.__dict__.iteritems():
          if isinstance(v, Schema):
            if v.objtype == SELF:
              v.objtype = self.__class__

            # has default?
            if isinstance(v, Single) and v.default:
              self._doc['data'][v.prd] = [{"type": v.objtype, "value":v.default}]

      def save(self):
        self._db[self._uri] = self._doc
        self._callback(self._uri)
        return self

      def remove(self):
        self._db.graph.remove(self._uri)

      def __setattr__(self, key, value):      
        try:
          obj = object.__getattribute__(self, key)
          if isinstance(obj, Single):

            objtype = "uri"      if hasattr(obj.objtype, "_db" ) else obj.objtype
            value   = value._uri if hasattr(value,       "_uri") else value

            self._doc['data'][obj.prd] = [{"type": objtype, "value": value}]
          elif isinstance(obj, Multiple):
            raise Exception("Cannot assign values to Multiple, use add()")
          else:
            object.__setattr__(self, key, value)
        except AttributeError:
          object.__setattr__(self, key, value)

      def _get(self, key):
        # convenience getattr without API conciderations.
        return object.__getattribute__(self, key)

      def __getattribute__(self, key):
        obj = object.__getattribute__(self, key)

        if isinstance(obj, Single):
          value = self._doc['data'][obj.prd][0]['value']

          try:
            return obj.objtype(value)
          except TypeError:
            return value

        elif isinstance(obj, Multiple):
          obj.parent = self
          return obj
        else: # standard object members
          return obj

      @classmethod
      def get(self, **kwargs):
        return self.getsorted(None, **kwargs)

      @classmethod
      def getsorted(self, sortby, **kwargs):
        candidates = []
        final = []
        restrictions = []

        # setup restriction list
        for k,v in kwargs.iteritems():
          restrictions.append([getattr(self,k).prd, v._uri if hasattr(v, "_uri") else v])

        for k, v in self.__dict__.iteritems():
          if isinstance(v, Single) and v.default:
            restrictions.append([v.prd, v.default])

        # get them resources
        if not restrictions:
          raise Error("Query without restrictions")

        # if sorting:
        if sortby:
          get_key = None
          view = reference.sortview(sortby)

        else:
          get_key = restrictions.pop()
          view = '_view/index/po'

        if get_key:
          for x in self._db.view(view, None, key=get_key):
            candidates.append(x.value)
        else:
          for x in self._db.view(view):
            candidates.append(x.value)

        for x in candidates:
          passed = 0
          for r in restrictions:
            try:
              for obj in x['data'][r[0]]:
                if obj['value'] == r[1]:
                  passed += 1
            except KeyError:
              pass

          if passed == len(restrictions):
            final.append(x)

        return [self(x["_id"], x) for x in final]        

    ## continuation of class Database __init__ here
    self.Resource = _Resource

  ## direct database methods

  def register_save_callback(self, callback):
    self.callbacks.append(callback)

  def callback(self, uri):
    for x in self.callbacks:
      x(uri)

  # def dump(self):
  #   return self.graph.get()

  def sortview(self, prd):
    hashed = hash(prd)

    if self.sortviewcache.has_key(hashed):
      return self.sortviewcache[hashed]

    view_id = str(hashed)

    if not self._db.__contains__(view_id):
      self._db["_design/"+view_id] = {"views": {
          "view" : {"map": "function(doc) {"+
                    "         for (x in doc.data) {"+
                    "           if (x == \""+prd+"\") {"+
                    "             emit(-doc.data[x][0].value, doc)}}}"}}}
      
    view_path = view_id + "/view"
    self.sortviewcache[hashed] = view_path
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
      if not self._db._db.has_key('_try'):
        break
      _try = uri + "_" + str(count)
      count += 1
    return _try

class Schema(object):
  pass

class Single(Schema):
  def __init__(self, prd, objtype=LITERAL, default=None):
    self.prd     = prd
    self.objtype = objtype
    self.default = default

class Multiple(Schema):
  def __init__(self, prd, objtype):
    self.parent  = None # gets set on access.
    self.prd     = prd
    self.objtype = objtype
    
  def add(self, value):
    try:
      data = self.parent._doc['data'][self.prd]
    except KeyError:
      data = []

    objtype = "uri"      if hasattr(self.objtype, "_db" ) else self.objtype
    value   = value._uri if hasattr(value,        "_uri") else value

    if data:
      for x in data:
        if x['value'] == value:
          # already there!
          return

    data.append({"type": objtype, "value":value})

    self.parent._doc['data'][self.prd] = data

  def get(self):
    try:
      data = self.parent._doc['data'][self.prd]
    except KeyError:
      data = []

    # TODO, maybe add bulk read?
    if hasattr(self.objtype, "_db"):
      return [self.objtype(x['value']) for x in data]
    else:
      return [self.parent._db._Resource(x['value']) for x in data]
    
