"""
The :mod:`layer.shapefile` module provides support for Shapefile access.
"""

from os import path
from java import net
from geoscript import util
from geoscript.layer import Layer
from geoscript.feature import feature 
from org.geotools.data import Transaction

class Shapefile(Layer):
  """
  A subclass of :class:`Layer <geoscript.layer.layer.Layer>` for the Shapefile format.

  *file* is the path to the Shapefile as a ``str``.
  """
  def __init__(self, file, workspace=None, fs=None):
    if workspace:
        Layer.__init__(self,workspace=workspace,fs=fs)
    else:
        f = util.toFile(file) 
        name = path.splitext(path.basename(file))[0]

        # circular deps
        from geoscript.workspace import Directory
        Layer.__init__(self, name, Directory(f.canonicalFile.parent))

  def getfile(self):
    return self.fs.dataStore.info.source.toURL().file

  def add(self,o):
    features = None
    if isinstance(o, Layer):
      features = o.features()
    elif isinstance(o, feature.Feature):
      features = [ o ]
    elif isinstance(o, (dict,list)):
      # @todo violating layer protocol
      if isinstance(o, list) and isinstance(o[0], (list,tuple)):
        # annoying, unpack tuple into list
        features = [ self.schema.feature(list(i)) for i in o ] 
      else:
        features = [ self.schema.feature(o) ]

    writer = self._source.getDataStore().getFeatureWriter( self.schema.getname(), Transaction.AUTO_COMMIT )

    for f in features:
      if not f.schema:
        f.schema = self.schema
      nf = writer.next()
      nf.setAttributes(f.values())
      writer.write()

    writer.close()


  file = property(getfile, None, None, 'Returns the file path to the Shapefile')

