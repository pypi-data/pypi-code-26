INCLUDEOPT = ('I', 'include-conf', [], 'include configuration(s)')
EXCLUDEOPT = ('X', 'exclude-conf', [], 'exclude configuration(s)')
ROOTPATHOPT = ('', 'root-path', '',
               'root path for the layouts (default to configuration root)')
PULLURIOPT = ('p', 'use-hgrc-path', '',
              'distant repository path name registered into hgrc.paths.*')
URIMAPOPT = ('', 'uri-map-file', '', 'specify uri map file')

DEFAULTOPTS = [INCLUDEOPT, EXCLUDEOPT, ROOTPATHOPT]
REMOTEOPTS = [PULLURIOPT, URIMAPOPT]
