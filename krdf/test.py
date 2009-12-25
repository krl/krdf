# -*- encoding:utf-8 -*-

import krdf
from krdf import Single, Multiple

rdf     = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf    = krdf.Namespace("http://xmlns.com/foaf/0.1/")
mytag   = krdf.Namespace("mytag:")

class Person(krdf.Resource):
  type        = Single(rdf.type, krdf.uri, foaf.Person)
  name        = Single(foaf.name)
  depiction   = Single(foaf.depiction, krdf.literal)
  friends     = Multiple(foaf.friend, krdf.SELF)

x = Person(mytag.Kristoffer)
x.name = "kristoffer"
x.depiction = "unicöde"
x.commit()

y = Person(mytag.Kristoffer)
y.name = "Mumin"
y.depiction = "lillmumin"
y.commit()

for x in Person.get():
  print "-"*100
  print x.type
  print x.name
  print x.depiction
