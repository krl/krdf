URI     = "uri"
LITERAL = "literal"
NUMBER  = "number"
SELF    = "self"

class Resource(object):
  # make an instance of this resource
  # this object should have a superclass that defines
  # a reference to its parent database object (self._ref)
  def __init__(self, uri, doc = None):    
    self._uri = uri
    self._doc = doc

    if not self._doc:
      self._doc = self._ref.get_doc(uri) #dict(self.db[uri])

    # loop through the schema items set in (sub)class definition
    for k, v in self.__class__.__dict__.iteritems():
      if isinstance(v, Schema):
        if v.objclass == SELF:
          v.objclass = self.__class__

        # has default?
        if isinstance(v, Single) and v.default:
          self._doc['data'][v.prd] = [{"type": v.objtype, "value":v.default}]

  def __eq__(self, other):
    return self._uri == other._uri

  def save(self):
    self._ref.save(self._uri)
    self._ref.trigger_callback(self._uri)
    return self

  def __setattr__(self, key, value):      
    try:
      obj = object.__getattribute__(self, key)
      if isinstance(obj, Single):

        objtype = "uri"      if hasattr(obj.objtype, "db"  ) else obj.objtype
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
      if not self._doc['data'].has_key(obj.prd):
        if obj.objtype == LITERAL:
          return ""
            
      return obj.objclass(self._doc['data'][obj.prd][0]['value'])

    elif isinstance(obj, Multiple):      
      return MultipleInterface(self._doc, obj)
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

    if not restrictions:
      raise Exception("Query without restrictions")

    # if sorting:
    if sortby:
      get_key = None
      view = self._ref.sortview(sortby)
    else:
      get_key = restrictions.pop()
      view = '_view/index/po'

    if get_key:
      for x in self._ref.db.view(view, None, key=get_key):
        candidates.append(x.value)
    else:
      for x in self._ref.db.view(view):
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

def Echo(value):
  return value

class Schema(object):
  def __init__(self, prd, objtype):
    self.prd      = prd
    
    if objtype == SELF: # SELF needs to be set from the init function
      self.objtype = URI
      self.objclass = SELF
    else:
      isobject = False
      if type(objtype) != str:
        isobject = True

      self.objclass = objtype if isobject else Echo
      self.objtype  = URI     if isobject else objtype

class Single(Schema):
  def __init__(self, prd, objtype=LITERAL, default=None):
    self.default  = default
    Schema.__init__(self, prd, objtype)

class Multiple(Schema):
  pass
    
class MultipleInterface():
  def __init__(self, doc, schema):
    self.doc = doc
    self.schema = schema

  def remove(self, what):
    try:
      data = self.doc['data'][self.schema.prd]
    except KeyError:
      return # empty means not there

    value = what._uri if hasattr(what, "_uri") else what

    final = []
    #check for duplicates
    for x in data:
      if x['value'] != value:
        final.append(x)

    if len(final) != len(data):
      self.doc['data'][self.schema.prd] = final

  def add(self, what):
    try:
      data = self.doc['data'][self.schema.prd]
    except KeyError:
      data = []

    value = what._uri if hasattr(what, "_uri") else what

    #check for duplicates
    for x in data:
      if x['value'] == value:
        return

    data.append({"type": self.schema.objtype, "value": value})

    self.doc['data'][self.schema.prd] = data

  def get(self):
    return [self.schema.objclass(x['value']) for x in self.doc['data'][self.schema.prd]]
