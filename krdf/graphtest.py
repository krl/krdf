# -*- encoding:utf-8 -*-

from graph import Graph

g = Graph("testgraph")

g.add("mytag:Kristoffer", "foaf:name", "Kristoffer", "l")
g.add("mytag:Kristoffer", "foaf:depiction", "rymdmöi", "l")

#g.remove("mytag:Kristoffer", "foaf:name")
g.set("mytag:Kristoffer", "foaf:depiction", "eh", "l")

print g.filter("mytag:Kristoffer")
