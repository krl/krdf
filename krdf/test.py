# -*- encoding:utf-8 -*-
import krdf
from krdf import Single, Multiple

import unittest

rdf   = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf  = krdf.Namespace("http://xmlns.com/foaf/0.1/")
mytag = krdf.Namespace("mytag:")

class TestAll(unittest.TestCase):
  def setUp(self):
    self.db = krdf.Database('http://localhost:5984/','test', True)

  def test_namespaces(self):
    self.assertEqual(rdf.test, str(rdf) + "test")

  def test_single(self):
    class AttributeTest(self.db.Resource):
      pass #no attributes

    test = AttributeTest(mytag.test)
    self.assertRaises(AttributeError, lambda: test.value)

  def test_single_literal(self):
    class LiteralTest(self.db.Resource):
      value = Single(mytag.testvalue)

    test1 = LiteralTest(mytag.test)
    test2 = LiteralTest(mytag.test)

    test1.value = "eh"
    self.assertEqual(test1.value, "eh", "single literal not cached") # should cache
    self.assertEqual(test2.value, "")   # same resource, another instance.

    test1.save()
    self.assertEqual(test2.value, "eh")   # should now have the update

  def test_single_decimal(self):
    class DecimalTest(self.db.Resource):
      value = Single(mytag.testvalue, krdf.DECIMAL)

    test = DecimalTest(mytag.dectest)
    test.value = 100
    test.save()
    # overwrite
    test = DecimalTest(mytag.dectest)

    self.assertEqual(type(test.value), int, "integers not preserved") # should cache

  def test_single_uri_fixed(self):
    class UriTest(self.db.Resource):
      type  = Single(rdf.type, krdf.URI, foaf.Person)

    test = UriTest(mytag.test)

    self.assertEqual(test.type, foaf.Person)

  def test_single_reference(self):
    class Referred(self.db.Resource):
      value = Single(mytag.testvalue)

    class Referrer(self.db.Resource):
      reference = Single(mytag.testvalue, Referred)

    referred = Referred(mytag.referred)
    referrer = Referrer(mytag.referreoor)

    referrer.reference = referred
    referrer.reference.value = "wobbah"
    referrer.reference.save()

    self.assertEqual(referred.value, "wobbah")    

if __name__ == '__main__':
  unittest.main()

# class Person(db.Resource):
#   type        = Single(rdf.type, krdf.uri, foaf.Person)
#   name        = Single(foaf.name)
#   depiction   = Single(foaf.depiction)
#   friends     = Multiple(foaf.friend, krdf.SELF)

# class Test(db.Resource):
#   type        = Single(rdf.type, krdf.uri, mytag.Test)
#   person      = Single(mytag.testperson, Person)

# for x in Person.get():
#   x.remove()

# krl = Person(mytag.Kristoffer)
# krl.name = "kristoffer"
# krl.depiction = "unicöde"
# krl.save()

# test = Test(mytag.Test)
# test.person = krl
# test.save()

# mum = Person(mytag.Mumin)
# mum.name = "Mumin"
# mum.depiction = "muminbild"
# mum.friends.add(krl)
# mum.save()

# for x in Person.get():
#   print "-"*100
#   print x.type
#   print x.name
#   print x.depiction
#   friends = x.friends.get()
#   if friends:
#     print "friends:"
#   for y in friends:
#     print "  " + y.name


# print "name", test.person.name

# test.person.name = "eh"
# print test.person
# test.person.save()

# print "name", test.person.name
