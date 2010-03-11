#krdf
Experimental, persisting RDF object mapping using couchdb for storage

#quick docs

First make sure you have a couchdb server up and running.

This creates the database object.

  import krdf
  from krdf import Single, Multiple

  db = krdf.Database('http://localhost:5984/','example', True)

Let's define a resource, this is done by subclassing the Resource class in our new db object.

We'll use the FOAF Person class as an example. first we need some namespaces.

  rdf  = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
  foaf = krdf.Namespace("http://xmlns.com/foaf/0.1/")	

  class Person(db.Resource):
    type        = Single(rdf.type, krdf.URI, foaf.Person)
    name        = Single(foaf.name, krdf.LITERAL)
    depiction   = Single(foaf.depiction)
    friends     = Multiple(foaf.friend, krdf.SELF)

The Single, Multiple objects are schema constructors. The Single constructor takes three arguments, the predicate, the object type, and the default.

type is thus rdf:type having URI type, and the default value of foaf:Person.

name and depiction has no default, but name is of krdf.LITERAL type.

the Multiple takes only predicate and type, here the type is a special symbol krdf.SELF, which refers to the class being defineditself, Persons have other Persons as friends. This is to get around circular class definition reference.

Let's now create a person
  
  me = Person("some-uri/Me")
  me.name = "Kristoffer"
  me.depiction = "http://rymdkoloni.se/moi.jpg"
  me.save()

The save method writes the changes to the database.

now we can restart the program and have

  me = Person("some-uri/Me")
  print me.name

  > Kristoffer

  A friend would be nice

  mumin = Person("some-uri/Mumin")
  mumin.name = "Mumin"
  mumin.depiction = "http://rymdkoloni.se/mumin.gif"
  mumin.friends.add(me)
  mumin.save()

  me.friends.add(mumin)
  me.save()

Notice how the Multiple schema cannot be directly assigned but must use the add() or remove() methods.

Now we can do:

  for x in me.friends.get():
    print x.name

And we get the name of our friend!