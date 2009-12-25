# -*- encoding:utf-8 -*-

from graph import Graph

g = Graph("test")

g.remove("mytag:Mumin")
g.remove("mytag:Kristoffer")

g.add("mytag:Kristoffer", "foaf:name", "Kristoffer", "l")
g.add("mytag:Kristoffer", "foaf:depiction", "rymdmoi", "l")

g.add("mytag:Mumin", "foaf:name", "Mumin", "l")
g.add("mytag:Mumin", "foaf:depiction", "gulle", "l")

#g.remove("mytag:Kristoffer", "foaf:name")
# g.set("mytag:Kristoffer", "foaf:depiction", "eh", "l")

# print g.filter("mytag:Kristoffer")

g.set("mytag:Kristoffer", "foaf:name", "farfar", "l")

for x in g.get("mytag:Kristoffer"):
  print x
