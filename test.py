from krdf import *

rdf     = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf    = Namespace("http://xmlns.com/foaf/0.1/")
nodetag = Namespace("tag:rymdkoloni.se,2009-07-13:")
rhzm    = Namespace("http://rymdkoloni.se/rhzm/0.1/")

class Person(Resource):
  type      = Single(rdf.type, foaf.Person, uri)
  name      = Single(foaf.name)
  depiction = Single(foaf.depiction)

x = Person(nodetag.Kristoffer)

class Note(Resource):
  type  = Single(rdf.type, rhzm.Note, uri)
  maker = Single(foaf.maker, None, Person)
  body  = Single(rhzm.body)

note = Note(nodetag.mulle)

print note.maker.name

#print x.name
#print x.depiction

# note.maker = x

# x.name      = "Kristoffer"
# x.depiction = "http://rymdkoloni.se/moi.jpg"

#x.commit()
