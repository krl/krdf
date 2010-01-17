# -*- Mode: Espresso; -*-

###########################################################################################
# hack with python comment syntax to be able to edit in espresso js-mode
# the [2:] slicing removes the first " \"" that python sees

index = {"views":{"po": {"map":(""" "#))))

function(doc) {
  for(x in doc.data) { 
    for(y in doc.data[x]) {
      emit([x, doc.data[x][y]['value']], doc);
    }
  }
}
"""#"
)[8:]}}}

###########################################################################################
# FIXME, at the moment this does reverse ordering of numbers only. (for latest first stuff)

sorting = (""" "#)

function(doc) {
  for (x in doc.data) {
    if (x == "%s") {
      emit(-doc.data[x][0].value, doc);
    }
  }
}

""" #"
)[5:]
