# -*- encoding:utf-8 -*-
import krdf

from krdf import Single, Multiple

import unittest

rdf   = krdf.Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
foaf  = krdf.Namespace("http://xmlns.com/foaf/0.1/")
testtag = krdf.Namespace("testtag:")

db = krdf.Database('http://localhost:5984/','unittest', True)

class TestNamespaces(unittest.TestCase):
  def test_namespaces(self):
    self.assertEqual(rdf.test, str(rdf) + "test")
        
class TestResource(unittest.TestCase):
  def test_single(self):
    class AttributeTest(db.Resource):
      pass #no attributes

    test = AttributeTest(testtag.test)
    self.assertRaises(AttributeError, lambda: test.nonvalue)

  def test_resource_equality(self):
    test1 = db.Resource(testtag.literaltest)
    test2 = db.Resource(testtag.literaltest)

    self.assertEqual(test1, test2)

  def test_type_equality(self):
    class Specialized(db.Resource):
      pass

    test1 = Specialized(testtag.literaltest)
    test2 = db.Resource(testtag.literaltest)

    self.assertEqual(test1, test2)

  def test_save(self):
    class SaveTest(db.Resource):
      value = Single(testtag.testvalue)

    s = SaveTest(testtag.savetest)
    s.value = "saved"
    s.save()

    self.assertEqual(s.value, "saved")

    db.clear_cache()

    self.assertEqual(s.value, "saved", "not same after cache clear")
    
  def test_literal_equality(self):
    class LiteralTest(db.Resource):
      value = Single(testtag.testvalue)

    test1 = LiteralTest(testtag.literaltest)
    test2 = LiteralTest(testtag.literaltest)

    test1.value = "eh"
    self.assertEqual(test1.value, "eh") 
    self.assertEqual(test1.value, test2.value) # same resource

  def test_single_uri_fixed(self):
    class UriTest(db.Resource):
      type  = Single(rdf.type, krdf.URI, foaf.Person)

    test = UriTest(testtag.test)
    self.assertEqual(test.type, foaf.Person)

  def test_single_reference(self):
    class Referred(db.Resource):
      value = Single(testtag.testvalue)

    class Referrer(db.Resource):
      reference = Single(testtag.testvalue, Referred)

    referred = Referred(testtag.referred)
    referred.save()

    referrer = Referrer(testtag.referreoor)
    referrer.reference = referred
    referrer.reference.value = "wobbah"
    referrer.reference.save()

    self.assertEqual(referred.value, referrer.reference.value)

  def test_multiple(self):
    class Friend(db.Resource):
      name       = Single(testtag.name)
      friends    = Multiple(testtag.friend, krdf.SELF)

    a = Friend(testtag.friend_a)
    a.name = "friend a"
    a.save()

    b = Friend(testtag.friend_b)
    b.name = "friend b"
    b.save()

    c = Friend(testtag.friend_c)
    c.name = "friend c"
    c.save()

    a.friends.add(b)
    a.friends.add(c)
    a.friends.add(c) # double add

    self.assertEqual([x.name for x in a.friends.get()], ["friend b", "friend c"])

    a.friends.remove(c)

    self.assertEqual(a.friends.get(), [b])

if __name__ == '__main__':
  unittest.main()
