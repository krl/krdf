import krdf
from krdf import Single, Multiple

rdf     = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf    = krdf.Namespace("http://xmlns.com/foaf/0.1/")
mytag   = krdf.Namespace("mytag:")
example = krdf.Namespace("example:")

db = krdf.Database('http://localhost:5984/','test2', True)

class Person(db.Resource):
  type       = Single(rdf.type, krdf.URI, foaf.Person)
  name       = Single(foaf.name)
  depiction  = Single(foaf.depiction, krdf.LITERAL)
  friends    = Multiple(foaf.friend, krdf.SELF)

class Message(db.Resource):
  type       = Single(rdf.type, krdf.URI, example.Message)
  maker      = Single(foaf.maker, Person)
  to         = Single(example.to   , Person)
  body       = Single(example.body)
  created    = Single(example.created, krdf.NUMBER)

k = Person("krill")
k.name = "Kristoffer"
k.depiction = "bild"

m = Person("mumin")
m.name = "Mumin"

# let's be friends forever
# m.friends.add(k)
# k.friends.add(m)

# save to database
k.save()
m.save()

# # fight!

rude = Message("rude")
rude.maker = m
rude.to = k
rude.body = "Gosh you're fat!"
rude.created = 100 #long time ago...
rude.save()

futurum = Message("future")
futurum.maker = k
futurum.to = k
futurum.body = "swoosh"
futurum.created = 1000
futurum.save()

reply = Message("reply")
reply.maker = k
reply.to = m
reply.body = "I forgive you."
reply.created = 120 # took me only 20 seconds to forgive!
reply.save()

# now we want these in order!
for x in Message.getsorted(example.created):
  print "["+str(x.created)+"]", x.maker.name, "->", x.to.name, ":", x.body
