import config.package

class Configure(config.package.Package):
  def __init__(self, framework):
    config.package.Package.__init__(self, framework)
    return

  def __str__(self):
    return ''

  def setupHelp(self,help):
    return

  def setupDependencies(self, framework):
    config.package.Package.setupDependencies(self, framework)
    self.compilers       = framework.require('config.compilers', self)
    return

  def configure(self):
    self.lib   = self.compilers.flibs
    self.dlib  = self.compilers.flibs
    self.found = 1
    return
