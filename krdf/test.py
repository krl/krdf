# -*- encoding:utf-8 -*-
import krdf
from krdf import Single, Multiple

rdf     = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf    = krdf.Namespace("http://xmlns.com/foaf/0.1/")
mytag   = krdf.Namespace("mytag:")

db = krdf.Database('http://localhost:5984/','test')

class Person(db.Resource):
  type        = Single(rdf.type, krdf.uri, foaf.Person)
  name        = Single(foaf.name)
  depiction   = Single(foaf.depiction)
  friends     = Multiple(foaf.friend, krdf.SELF)

for x in Person.get():
  x.remove()

krl = Person(mytag.Kristoffer)
krl.name = "kristoffer"
krl.depiction = "unicöde"
krl.commit()

mum = Person(mytag.Mumin)
mum.name = "Mumin"
mum.depiction = "muminbild"
mum.friends.add(krl)
mum.commit()

kaka = Person(mytag.Kaka)
kaka.name = "kaka"
kaka.depiction = "kakbild"
kaka.friends.add(krl)
kaka.friends.add(mum)
kaka.commit()

for x in Person.get():
  print "-"*100
  print x.type
  print x.name
  print x.depiction
  friends = x.friends.get()
  if friends:
    print "friends:"
  for y in friends:
    print "  " + y.name

