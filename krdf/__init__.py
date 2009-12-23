"""
A pythonic rdf persistance layer on top of python-tokyocabinet
Python 2.4+ is needed.
"""
from krdf import Namespace, Resource, Single, Multiple, dumpdb, makeuri, uri, literal, decimal, register_commit_callback, tojson, fromjson, fromdict, SELF

__version__ = '0.0.1'
