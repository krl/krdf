import krdf
from krdf import Single, Multiple

rdf     = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf    = krdf.Namespace("http://xmlns.com/foaf/0.1/")
mytag   = krdf.Namespace("testtag:")

class Person(krdf.Resource):
  type        = Single(rdf.type, krdf.uri, foaf.Person)
  name        = Single(foaf.name)
  depiction   = Single(foaf.depiction, krdf.literal, "/inc/unknown.png")
  friends     = Multiple(foaf.friend, krdf.SELF)

x = Person(mytag.Kristoffer)

x.name = "kristoffer"
x.commit()

y = Person(mytag.Mumin)

y.name = "mumin"
y.commit()

# x.name = "Kristoffer"
# x.depiction = "Test"
# x.commit()

# print x.name
# print x.depiction

for x in Person.get():
  print "-"*100
  print x.type
  print x.name
  print x.depiction
