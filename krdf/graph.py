# -*- encoding:utf-8 -*-

from bsddb3 import db
import cPickle as pickle

################################
# graph class

class Graph ():
  def __init__(self, filename):
    self.db = db.DB()
    self.db.open(filename, None, db.DB_HASH, db.DB_CREATE)

  def add(self, s, p, o, t):
    data = pickle.dumps({'s': s, 'p': p, 'o': o, 't': t})

    # index it.
    for x, y in [("S", s), ("P", p), ("O", o)]:
      try:
        index = pickle.loads(self.db[x+y])
        index.add(data)
        self.db[x+y] = pickle.dumps(index)
      except KeyError:
        self.db[x+y] = pickle.dumps(set([data]))

  def remove(self, s=None, p=None, o=None):
    for tid in self.filter(s,p,o):
      triple = pickle.loads(tid)
      for x in ["s", "p", "o"]:
        try:
          index = pickle.loads(self.db[x.upper()+triple[x]])
          index.remove(tid)
          self.db[x.upper()+triple[x]] = pickle.dumps(index)      
        except KeyError:
          pass

  def set(self, s, p, o, t):
    self.remove(s, p, None)
    self.add(s, p, o, t)

  def filter(self, s=None, p=None, o=None):
    sets = []
    for x, y in [("S", s), ("P", p), ("O", o)]:
      if y:
        try:
          # unpickle the index set
          sets.append(pickle.loads(self.db[x+y]))
        except KeyError: # if not in index
          pass
    if sets:      
      return sets[0].intersection(*sets[1:])
    else:
      return set([])

  def get(self, s=None, p=None, o=None):
    return [pickle.loads(x) for x in self.filter(s, p, o)]  

