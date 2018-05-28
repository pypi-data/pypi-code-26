# -*- coding: utf-8 -*-
"""\
* *[Summary]* ::  A /library/ to support icmsPkg facilities
"""

####+BEGIN: bx:icm:python:top-of-file :partof "bystar" :copyleft "halaal+minimal"
"""
*  This file:/acct/smb/com/dev-py/LUE/Sync/pypi/pkgs/unisos/common/dev/unisos/common/new-icmsPkgLib.py :: [[elisp:(org-cycle)][| ]]
** is part of The Libre-Halaal ByStar Digital Ecosystem. http://www.by-star.net
** *CopyLeft*  This Software is a Libre-Halaal Poly-Existential. See http://www.freeprotocols.org
** A Python Interactively Command Module (PyICM). Part Of ByStar.
** Best Developed With COMEEGA-Emacs And Best Used With Blee-ICM-Players.
** Warning: All edits wityhin Dynamic Blocks may be lost.
"""
####+END:


"""
*  [[elisp:(org-cycle)][| *Lib-Module-INFO:* |]] :: Author, Copyleft and Version Information
"""

####+BEGIN: bx:global:lib:name-py :style "fileName"
__libName__ = "icmsPkgLib"
####+END:

####+BEGIN: bx:global:timestamp:version-py :style "date"
__version__ = "201712242213"
####+END:

####+BEGIN: bx:global:icm:status-py :status "Production"
__status__ = "Production"
####+END:

__credits__ = [""]

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/update/sw/icm/py/icmInfo-mbNedaGpl.py"
icmInfo = {
    'authors':         ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"],
    'copyright':       "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]",
    'licenses':        ["[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"],
    'maintainers':     ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]",],
    'contacts':        ["[[http://mohsen.1.banan.byname.net/contact]]",],
    'partOf':          ["[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]",]
}
####+END:

####+BEGIN: bx:icm:python:topControls 
"""
*  [[elisp:(org-cycle)][|/Controls/| ]] :: [[elisp:(org-show-subtree)][|=]] [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]]
"""
####+END:

"""
* 
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/pythonWb.org"
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "pep8 %s" (bx:buf-fname))))][pep8]] | [[elisp:(python-check (format "flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]
####+END:
"""


####+BEGIN: bx:icm:python:section :title "ContentsList"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *ContentsList*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:


####+BEGIN: bx:dblock:python:icmItem :itemType "=Imports=" :itemTitle "*IMPORTS*"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || =Imports=      :: *IMPORTS*  [[elisp:(org-cycle)][| ]]
"""
####+END:

import os
import collections
import enum

# NOTYET, should become a dblock with its own subItem
from unisos import ucf
from unisos import icm

G = icm.IcmGlobalContext()
G.icmLibsAppend = __file__
G.icmCmndsLibsAppend = __file__
# NOTYET DBLOCK Ends -- Rest of bisos libs follow;


####+BEGIN: bx:dblock:python:section :title "Library Description (Overview)"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *Library Description (Overview)*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:python:icm:cmnd:classHead :modPrefix "new" :cmndName "icmsPkgLib_LibOverview" :parsMand "" :parsOpt "" :argsMin "0" :argsMax "3" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /icmsPkgLib_LibOverview/ parsMand= parsOpt= argsMin=0 argsMax=3 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class icmsPkgLib_LibOverview(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ ]
    cmndArgsLen = {'Min': 0, 'Max': 3,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        moduleDescription="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Description:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Xref]          :: *[Related/Xrefs:]*  <<Xref-Here->>  -- External Documents  [[elisp:(org-cycle)][| ]]

**  [[elisp:(org-cycle)][| ]]	Model and Terminology 					   :Overview:
This module is part of BISOS and its primary documentation is in  http://www.by-star.net/PLPC/180047
**      [End-Of-Description]
"""
        
        moduleUsage="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Usage:* | ]]

**      How-Tos:
**      [End-Of-Usage]
"""
        
        moduleStatus="""
*       [[elisp:(org-show-subtree)][|=]]  [[elisp:(org-cycle)][| *Status:* | ]]
**  [[elisp:(org-cycle)][| ]]  [Info]          :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
** TODO [[elisp:(org-cycle)][| ]]  Current         :: Just getting started [[elisp:(org-cycle)][| ]]
**      [End-Of-Status]
"""
        cmndArgsSpec = {"0&-1": ['moduleDescription', 'moduleUsage', 'moduleStatus']}
        cmndArgsValid = cmndArgsSpec["0&-1"]
        for each in effectiveArgsList:
            if each in cmndArgsValid:
                print each
                if interactive:
                    #print( str( __doc__ ) )  # This is the Summary: from the top doc-string
                    #version(interactive=True)
                    exec("""print({})""".format(each))
                
        return(format(str(__doc__)+moduleDescription))


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  pkgBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def pkgBaseDir_obtain():
    return os.path.abspath(
        ".."
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  pkgInfoBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def pkgInfoBaseDir_obtain():
    return os.path.abspath(
        "../pkgInfo"
    )


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  pkgInputsBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def pkgInputsBaseDir_obtain():
    return os.path.abspath(
        "../pkgInputs"
    )


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  pkgInfoFpBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def pkgInfoFpBaseDir_obtain(
    icmsPkgInfoBaseDir=None,
):
    if icmsPkgInfoBaseDir:
        return os.path.abspath(
            "{}/pkgInfo/fp".format(icmsPkgInfoBaseDir)
        )
    else:
        return os.path.abspath(
             "../pkgInfo/fp"
        )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  controlBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def controlBaseDir_obtain(
    icmsPkgInfoBaseDir=None,
):
    if icmsPkgInfoBaseDir:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot= os.path.abspath("{}/pkgInfo/fp".format(icmsPkgInfoBaseDir)),
                parName="icmsPkgControlBaseDir")
        )
    else:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot="../pkgInfo/fp",
                parName="icmsPkgControlBaseDir")
        )


def logBaseDir_obtain(
    icmsPkgInfoBaseDir=None,      
):
    if icmsPkgInfoBaseDir:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot= os.path.abspath("{}/pkgInfo/fp".format(icmsPkgInfoBaseDir)),
                parName="icmsPkgLogBaseDir")
        )
    else:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot="../pkgInfo/fp",
                parName="icmsPkgLogBaseDir")
        )


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  varBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def varBaseDir_obtain(
    icmsPkgInfoBaseDir=None,     
):
    if icmsPkgInfoBaseDir:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot= os.path.abspath("{}/pkgInfo/fp".format(icmsPkgInfoBaseDir)),
                parName="icmsPkgVarBaseDir")
        )
    else:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot="../pkgInfo/fp",
                parName="icmsPkgVarBaseDir")
        )


def varConfigBaseDir_obtain(
    icmsPkgInfoBaseDir=None,
):
    return(
        os.path.join(varBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "config")
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  tmpBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def tmpBaseDir_obtain(
    icmsPkgInfoBaseDir=None,     
):
    if icmsPkgInfoBaseDir:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot= os.path.abspath("{}/pkgInfo/fp".format(icmsPkgInfoBaseDir)),
                parName="icmsPkgTmpBaseDir")
        )
    else:
        return(
            icm.FILE_ParamValueReadFrom(
                parRoot="../pkgInfo/fp",
                parName="icmsPkgTmpBaseDir")
        )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF          ::  icmsBxoBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def icmsBxoBaseDir_obtain():
    return os.path.abspath(
        "../../.."
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || IIF          ::  icmsRunEnvBaseDir_obtain    [[elisp:(org-cycle)][| ]]
"""
def icmsRunEnvBaseDir_obtain():
    return icmsBxoBaseDir_obtain()


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *File Parameters Obtain*
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  icmsPkgName_fpObtain    [[elisp:(org-cycle)][| ]]
"""
def icmsPkgName_fpObtain(
        icmsPkgInfoBaseDir=None,
):
    """NOTYET -- Called obtain to leave Get for the IIF"""
    return icm.FILE_ParamValueReadFrom(
        parRoot=os.path.join(
            pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir),
        ),
        parName="icmsPkgName",
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  icmsPkgControlBaseDir_fpObtain    [[elisp:(org-cycle)][| ]]
"""
def icmsPkgControlBaseDir_fpObtain():
    """NOTYET -- Called obtain to leave Get for the IIF"""
    return icm.FILE_ParamValueReadFrom(
        parRoot=os.path.join(
            pkgInfoFpBaseDir_obtain(),            
        ),
        parName="icmsPkgControlBaseDir",        
    )



"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Common Arguments Specification*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  commonParamsSpecify    [[elisp:(org-cycle)][| ]]
"""
def commonParamsSpecify(
        icmParams,
):
    
    icmParams.parDictAdd(
        parName='icmsPkgName',
        parDescription="ICMs Package Name",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgName',
    )

    icmParams.parDictAdd(
        parName='icmsPkgInfoBaseDir',
        parDescription="ICMs Package Info Environment -- A BaseDir for var/log/tmp (bxo=current bxo)",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgInfoBaseDir',
    )
    
    icmParams.parDictAdd(
        parName='icmsPkgRunBaseDir',
        parDescription="ICMs Package Run Environment -- A BaseDir for var/log/tmp (bxo=current bxo)",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgRunBaseDir',
    )
    
    icmParams.parDictAdd(
        parName='icmsPkgControlBaseDir',
        parDescription="ICMs Package Control Base Directory",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgControlBaseDir',
    )
    
    icmParams.parDictAdd(
        parName='icmsPkgVarBaseDir',
        parDescription="ICMs Package Var Base Directory",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgVarBaseDir',
    )

    
    icmParams.parDictAdd(
        parName='icmsPkgLogBaseDir',
        parDescription="ICMs Package Log Base Directory",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgLogBaseDir',
    )

        
    icmParams.parDictAdd(
        parName='icmsPkgTmpBaseDir',
        parDescription="ICMs Package Tmp Base Directory",
        parDataType=None,
        parDefault=None,
        parChoices=["any"],
        parScope=icm.ICM_ParamScope.TargetParam,
        argparseShortOpt=None,
        argparseLongOpt='--icmsPkgTmpBaseDir',
    )


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Common Examples Sections*
"""
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  examples_pkgInfoPars    [[elisp:(org-show-subtree)][|=]]   [[elisp:(org-cycle)][| ]]
"""    
def examples_pkgInfoPars():
    """
** Auxiliary examples to be commonly used.
"""
    icm.cmndExampleMenuChapter('* =FP Values=  pkgInfo Parameters')

    cmndAction = " -i inMailAcctParsGet" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, verbosity='none')

    menuLine = """"""
    icm.cmndExampleMenuItem(menuLine, icmName="pkgManage.py", verbosity='none')    

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  examples_pkgInfoParsFull    [[elisp:(org-cycle)][| ]]
"""
def examples_pkgInfoParsFull(
    icmsPkgName,
    icmsPkgInfoBaseDir=None,
    icmsPkgControlBaseDir=None,
    icmsPkgRunBaseDir=None,
):
    """
** Auxiliary examples to be commonly used.
"""
    icm.cmndExampleMenuChapter(' =FP Values=  *pkgInfo Get Parameters*')

    cmndName = "pkgInfoParsGet" ; cmndArgs = "" ;
    cps = collections.OrderedDict() ;  cps['icmsPkgInfoBaseDir'] = icmsPkgInfoBaseDir 
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')

    # cmndAction = " -i pkgInfoParsGet" ; cmndArgs = ""
    # menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    # icm.cmndExampleMenuItem(menuLine, verbosity='none')

    icm.cmndExampleMenuChapter(' =FP Values=  *PkgInfo Defaults ParsSet  --*')

    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "bisosPolicy" ;
    cps = collections.OrderedDict() ; cps['icmsPkgName'] = icmsPkgName ; cps['icmsPkgControlBaseDir'] = icmsPkgControlBaseDir ; cps['icmsPkgInfoBaseDir'] = icmsPkgInfoBaseDir 
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    
    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "bxoPolicy" ;
    cps = collections.OrderedDict() ; cps['icmsPkgName'] = icmsPkgName ; cps['icmsPkgControlBaseDir'] = icmsPkgControlBaseDir 
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    
    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "runBaseDirPolicy" ;
    cps = collections.OrderedDict() ; cps['icmsPkgName'] = icmsPkgName
    cps['icmsPkgControlBaseDir'] = icmsPkgControlBaseDir ; cps['icmsPkgRunBaseDir'] = icmsPkgRunBaseDir
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    
    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "debianPolicy" ;
    cps = collections.OrderedDict() ; cps['icmsPkgName'] = icmsPkgName 
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    
    cmndName = "pkgInfoParsDefaultsSet" ; cmndArgs = "centosPolicy" ;
    cps = collections.OrderedDict() ; cps['icmsPkgName'] = icmsPkgName 
    icm.ex_gCmndMenuItem(cmndName, cps, cmndArgs, verbosity='little')
    

    icm.cmndExampleMenuChapter(' =FP Values=  *PkgInfo ParsSet -- Set Parameters Explicitly*')

    cmndAction = " -i pkgInfoParsSet" ; cmndArgs = ""
    menuLine = """--icmsPkgName="pkgName" {cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="echo", verbosity='none')

    cmndAction = " -i pkgInfoParsSet" ; cmndArgs = ""
    menuLine = """--icmsPkgControlBaseDir="path"  {cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="echo", verbosity='none')

    cmndAction = " -i pkgInfoParsSet" ; cmndArgs = ""
    varPath = os.path.join(icmsRunEnvBaseDir_obtain(), "var", icmsPkgName_fpObtain(
        icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))
    menuLine = """--icmsPkgVarBaseDir={varPath}  {cmndAction} {cmndArgs}""".format(
        varPath=varPath, cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="echo", verbosity='none')

    cmndAction = " -i pkgInfoParsSet" ; cmndArgs = ""
    tmpPath = os.path.join(icmsRunEnvBaseDir_obtain(), "tmp", icmsPkgName_fpObtain(
        icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))
    menuLine = """--icmsPkgTmpBaseDir={tmpPath}  {cmndAction} {cmndArgs}""".format(
        tmpPath=tmpPath, cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="echo", verbosity='none')
  
    icm.cmndExampleMenuChapter(' =RunEnv=  *Run Environment (BaseDirs) Setups/Clean*')    

    cmndAction = " -i icmsRunEnvsPreps" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="", verbosity='none')

    cmndAction = " -i icmsRunEnvsClean" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="", verbosity='none')

    icm.cmndExampleMenuChapter(' =RunEnv=  *SymLinks To var/log/tmp/ Setups/Clean*')    

    cmndAction = " -i icmsRunEnvsLinks" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="", verbosity='none')

    cmndAction = " -i icmsRunEnvsLinksClean" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="", verbosity='none')

    icm.cmndExampleMenuChapter(' =RunEnv=  *SymLinks To Libraries Setups/Clean*')    
    
    cmndAction = " -i icmsLibsLinks" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="", verbosity='none')

    cmndAction = " -i icmsLibsLinksClean" ; cmndArgs = ""
    menuLine = """{cmndAction} {cmndArgs}""".format(cmndAction=cmndAction, cmndArgs=cmndArgs)
    icm.cmndExampleMenuItem(menuLine, icmWrapper="", verbosity='none')
     

"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *File Parameters Get/Set -- Commands*
"""

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func         ::  FP_readTreeAtBaseDir_CmndOutput    [[elisp:(org-cycle)][| ]]
"""
def FP_readTreeAtBaseDir_CmndOutput(
        interactive,
        fpBaseDir,
        cmndOutcome,
):
    """Invokes FP_readTreeAtBaseDir.cmnd as interactive-output only."""
    #
    # Interactive-Output + Chained-Outcome Command Invokation
    #
    FP_readTreeAtBaseDir = icm.FP_readTreeAtBaseDir()
    FP_readTreeAtBaseDir.cmndLineInputOverRide = True
    FP_readTreeAtBaseDir.cmndOutcome = cmndOutcome
        
    return FP_readTreeAtBaseDir.cmnd(
        interactive=interactive,
        FPsDir=fpBaseDir,
    )


####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "pkgInfoParsGet" :comment "" :parsMand "" :parsOpt "icmsPkgInfoBaseDir" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pkgInfoParsGet/ parsMand= parsOpt=icmsPkgInfoBaseDir argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pkgInfoParsGet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'icmsPkgInfoBaseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        icmsPkgInfoBaseDir=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'icmsPkgInfoBaseDir': icmsPkgInfoBaseDir, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        icmsPkgInfoBaseDir = callParamsDict['icmsPkgInfoBaseDir']
####+END:

        FP_readTreeAtBaseDir_CmndOutput(
            interactive=interactive,
            fpBaseDir=pkgInfoFpBaseDir_obtain(
                icmsPkgInfoBaseDir=icmsPkgInfoBaseDir,
            ),
            cmndOutcome=cmndOutcome,
        )

        return cmndOutcome


    def cmndDesc(): """
** Without --icmsPkgInfoBaseDir, it reads from ../pkgInfo/fp.
"""


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  pkgInfoParsGetOLD    [[elisp:(org-cycle)][| ]]
"""
class pkgInfoParsGetOLD(icm.Cmnd):
    """
** Read File Parameters at pkgInfo/fp
"""

    cmndParamsMandatory = []
    cmndParamsOptional = ['icmsPkgInfoBaseDir',]       
    cmndArgsLen = {'Min': 0, 'Max': 0,}
    cmndArgsSpec = {}    

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par "icmsPkgInfoBaseDir" :args ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:
        #G = icm.IcmGlobalContext()

        FP_readTreeAtBaseDir_CmndOutput(
            interactive=interactive,
            fpBaseDir=pkgInfoFpBaseDir_obtain(),
            cmndOutcome=cmndOutcome,
        )

        return cmndOutcome

####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "pkgInfoParsSet" :comment "" :parsMand "" :parsOpt "icmsPkgInfoBaseDir icmsPkgName icmsPkgControlBaseDir icmsPkgVarBaseDir icmsPkgTmpBaseDir icmsPkgBasesPolicy icmsPkgLogBaseDir" :argsMin "0" :argsMax "0" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pkgInfoParsSet/ parsMand= parsOpt=icmsPkgInfoBaseDir icmsPkgName icmsPkgControlBaseDir icmsPkgVarBaseDir icmsPkgTmpBaseDir icmsPkgBasesPolicy icmsPkgLogBaseDir argsMin=0 argsMax=0 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pkgInfoParsSet(icm.Cmnd):
    cmndParamsMandatory = [ ]
    cmndParamsOptional = [ 'icmsPkgInfoBaseDir', 'icmsPkgName', 'icmsPkgControlBaseDir', 'icmsPkgVarBaseDir', 'icmsPkgTmpBaseDir', 'icmsPkgBasesPolicy', 'icmsPkgLogBaseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 0,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        icmsPkgInfoBaseDir=None,         # or Cmnd-Input
        icmsPkgName=None,         # or Cmnd-Input
        icmsPkgControlBaseDir=None,         # or Cmnd-Input
        icmsPkgVarBaseDir=None,         # or Cmnd-Input
        icmsPkgTmpBaseDir=None,         # or Cmnd-Input
        icmsPkgBasesPolicy=None,         # or Cmnd-Input
        icmsPkgLogBaseDir=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'icmsPkgInfoBaseDir': icmsPkgInfoBaseDir, 'icmsPkgName': icmsPkgName, 'icmsPkgControlBaseDir': icmsPkgControlBaseDir, 'icmsPkgVarBaseDir': icmsPkgVarBaseDir, 'icmsPkgTmpBaseDir': icmsPkgTmpBaseDir, 'icmsPkgBasesPolicy': icmsPkgBasesPolicy, 'icmsPkgLogBaseDir': icmsPkgLogBaseDir, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        icmsPkgInfoBaseDir = callParamsDict['icmsPkgInfoBaseDir']
        icmsPkgName = callParamsDict['icmsPkgName']
        icmsPkgControlBaseDir = callParamsDict['icmsPkgControlBaseDir']
        icmsPkgVarBaseDir = callParamsDict['icmsPkgVarBaseDir']
        icmsPkgTmpBaseDir = callParamsDict['icmsPkgTmpBaseDir']
        icmsPkgBasesPolicy = callParamsDict['icmsPkgBasesPolicy']
        icmsPkgLogBaseDir = callParamsDict['icmsPkgLogBaseDir']
####+END:

        #G = icm.IcmGlobalContext()        

        def createPathAndFpWrite(
                fpPath,
                valuePath,
        ):
            valuePath = os.path.abspath(valuePath)
            try:
                os.makedirs(valuePath)
            except OSError:
                if not os.path.isdir(valuePath):
                    raise
            
            icm.FILE_ParamWriteToPath(
                parNameFullPath=fpPath,
                parValue=valuePath,
            )

            
        if icmsPkgName:
            icm.FILE_ParamWriteToPath(
                parNameFullPath=os.path.join(pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "icmsPkgName"),
                parValue=icmsPkgName,
            )

        if icmsPkgBasesPolicy:
            icm.FILE_ParamWriteToPath(
                parNameFullPath=os.path.join(pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "icmsPkgBasesPolicy"),
                parValue=icmsPkgBasesPolicy,
            )

        if icmsPkgControlBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "icmsPkgControlBaseDir"),
                icmsPkgControlBaseDir,
            )

        if icmsPkgVarBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "icmsPkgVarBaseDir"),
                icmsPkgVarBaseDir,
            )

        if icmsPkgLogBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "icmsPkgLogBaseDir"),
                icmsPkgLogBaseDir,
            )
            
        if icmsPkgTmpBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir), "icmsPkgTmpBaseDir"),
                icmsPkgTmpBaseDir,
            )
            
        if interactive:
            icm.ANN_here("pkgInfoParsSet")

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )


    def cmndDesc(): """
** Doc String Outside Of Dblock.
"""
    

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  pkgInfoParsSet    [[elisp:(org-cycle)][| ]]
"""    
class pkgInfoParsSetOLD(icm.Cmnd):
    """
** Set File Parameters at ../pkgInfo/fp
"""

    cmndParamsMandatory = []
    cmndParamsOptional = ['icmsPkgName', 'icmsPkgControlBaseDir', 'icmsPkgVarBaseDir',
                         'icmsPkgTmpBaseDir', 'icmsPkgBasesPolicy', 'icmsPkgLogBaseDir']       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par "icmsPkgName icmsPkgBasesPolicy icmsPkgControlBaseDir icmsPkgVarBaseDir icmsPkgLogBaseDir icmsPkgTmpBaseDir"
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        icmsPkgName=None,         # or Cmnd-Input
        icmsPkgBasesPolicy=None,         # or Cmnd-Input
        icmsPkgControlBaseDir=None,         # or Cmnd-Input
        icmsPkgVarBaseDir=None,         # or Cmnd-Input
        icmsPkgLogBaseDir=None,         # or Cmnd-Input
        icmsPkgTmpBaseDir=None,         # or Cmnd-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'icmsPkgName': icmsPkgName, 'icmsPkgBasesPolicy': icmsPkgBasesPolicy, 'icmsPkgControlBaseDir': icmsPkgControlBaseDir, 'icmsPkgVarBaseDir': icmsPkgVarBaseDir, 'icmsPkgLogBaseDir': icmsPkgLogBaseDir, 'icmsPkgTmpBaseDir': icmsPkgTmpBaseDir, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        icmsPkgName = callParamsDict['icmsPkgName']
        icmsPkgBasesPolicy = callParamsDict['icmsPkgBasesPolicy']
        icmsPkgControlBaseDir = callParamsDict['icmsPkgControlBaseDir']
        icmsPkgVarBaseDir = callParamsDict['icmsPkgVarBaseDir']
        icmsPkgLogBaseDir = callParamsDict['icmsPkgLogBaseDir']
        icmsPkgTmpBaseDir = callParamsDict['icmsPkgTmpBaseDir']
####+END:

        #G = icm.IcmGlobalContext()        

        def createPathAndFpWrite(
                fpPath,
                valuePath,
        ):
            valuePath = os.path.abspath(valuePath)
            try:
                os.makedirs(valuePath)
            except OSError:
                if not os.path.isdir(valuePath):
                    raise
            
            icm.FILE_ParamWriteToPath(
                parNameFullPath=fpPath,
                parValue=valuePath,
            )

            
        if icmsPkgName:
            icm.FILE_ParamWriteToPath(
                parNameFullPath=os.path.join(pkgInfoFpBaseDir_obtain(), "icmsPkgName"),
                parValue=icmsPkgName,
            )

        if icmsPkgBasesPolicy:
            icm.FILE_ParamWriteToPath(
                parNameFullPath=os.path.join(pkgInfoFpBaseDir_obtain(), "icmsPkgBasesPolicy"),
                parValue=icmsPkgBasesPolicy,
            )

        if icmsPkgControlBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(), "icmsPkgControlBaseDir"),
                icmsPkgControlBaseDir,
            )

        if icmsPkgVarBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(), "icmsPkgVarBaseDir"),
                icmsPkgVarBaseDir,
            )

        if icmsPkgLogBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(), "icmsPkgLogBaseDir"),
                icmsPkgLogBaseDir,
            )
            
        if icmsPkgTmpBaseDir:
            createPathAndFpWrite(
                os.path.join(pkgInfoFpBaseDir_obtain(), "icmsPkgTmpBaseDir"),
                icmsPkgTmpBaseDir,
            )
            
        if interactive:
            icm.ANN_here("pkgInfoParsSet")

        return cmndOutcome.set(
            opError=icm.OpError.Success,
            opResults=None,
        )


####+BEGIN: bx:icm:python:cmnd:classHead :modPrefix "new" :cmndName "pkgInfoParsDefaultsSet" :comment "" :parsMand "icmsPkgName" :parsOpt "icmsPkgInfoBaseDir icmsPkgControlBaseDir icmsPkgRunBaseDir" :argsMin "0" :argsMax "1" :asFunc "" :interactiveP ""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || ICM-Cmnd       :: /pkgInfoParsDefaultsSet/ parsMand=icmsPkgName parsOpt=icmsPkgInfoBaseDir icmsPkgControlBaseDir icmsPkgRunBaseDir argsMin=0 argsMax=1 asFunc= interactive=  [[elisp:(org-cycle)][| ]]
"""
class pkgInfoParsDefaultsSet(icm.Cmnd):
    cmndParamsMandatory = [ 'icmsPkgName', ]
    cmndParamsOptional = [ 'icmsPkgInfoBaseDir', 'icmsPkgControlBaseDir', 'icmsPkgRunBaseDir', ]
    cmndArgsLen = {'Min': 0, 'Max': 1,}

    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        icmsPkgName=None,         # or Cmnd-Input
        icmsPkgInfoBaseDir=None,         # or Cmnd-Input
        icmsPkgControlBaseDir=None,         # or Cmnd-Input
        icmsPkgRunBaseDir=None,         # or Cmnd-Input
        argsList=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome
            effectiveArgsList = G.icmRunArgsGet().cmndArgs
        else:
            effectiveArgsList = argsList

        callParamsDict = {'icmsPkgName': icmsPkgName, 'icmsPkgInfoBaseDir': icmsPkgInfoBaseDir, 'icmsPkgControlBaseDir': icmsPkgControlBaseDir, 'icmsPkgRunBaseDir': icmsPkgRunBaseDir, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        icmsPkgName = callParamsDict['icmsPkgName']
        icmsPkgInfoBaseDir = callParamsDict['icmsPkgInfoBaseDir']
        icmsPkgControlBaseDir = callParamsDict['icmsPkgControlBaseDir']
        icmsPkgRunBaseDir = callParamsDict['icmsPkgRunBaseDir']
####+END:
        #G = icm.IcmGlobalContext()

        #basesPolicyChoices = self.__class__.cmndArgsSpec[0]

        basesPolicy = effectiveArgsList[0]

        if not basesPolicy:
            basesPolicy = G.icmRunArgsGet().cmndArgs[0]

        print basesPolicy
        print icmsPkgInfoBaseDir

        pkgInfoParsSet().cmnd(
            interactive=False,
            icmsPkgInfoBaseDir=icmsPkgInfoBaseDir,
            icmsPkgName=icmsPkgName,  
        )

        if basesPolicy == "bisosPolicy":
            if not icmsPkgControlBaseDir:
                return icm.EH_problem_usageError("Missing Control BaseDir")

            controlPath = icmsPkgControlBaseDir
            varPath = os.path.join("/bisos", "var")
            logPath = os.path.join("/bisos", "log")            
            tmpPath = os.path.join("/bisos", "tmp")

        elif basesPolicy == "bxoPolicy":
            if not icmsPkgControlBaseDir:
                return icm.EH_problem_usageError("")

            controlPath = icmsPkgControlBaseDir
            varPath = os.path.join(icmsRunEnvBaseDir_obtain(), "var", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))
            logPath = os.path.join(icmsRunEnvBaseDir_obtain(), "log", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))            
            tmpPath = os.path.join(icmsRunEnvBaseDir_obtain(), "tmp", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))

        elif basesPolicy == "runBaseDirPolicy":
            if not icmsPkgRunBaseDir:
                return icm.EH_problem_usageError("")
            
            if icmsPkgControlBaseDir:
                controlPath = icmsPkgControlBaseDir
            else:
                controlPath = os.path.join(icmsPkgRunBaseDir, "control", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))

            varPath = os.path.join(icmsPkgRunBaseDir, "var", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))
            logPath = os.path.join(icmsPkgRunBaseDir, "log", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))            
            tmpPath = os.path.join(icmsPkgRunBaseDir, "tmp", icmsPkgName_fpObtain(icmsPkgInfoBaseDir=icmsPkgInfoBaseDir))
            
        elif basesPolicy == "debianPolicy":
            controlPath = os.path.join("/etc/bystar", icmsPkgName)
            varPath = os.path.join("/var/lib/bystar/", icmsPkgName)
            logPath = os.path.join("/var/log/bystar/", icmsPkgName)            
            tmpPath = os.path.join("/tmp/bystar", icmsPkgName)
            
        elif basesPolicy == "centosPolicy":
            controlPath = os.path.join("/etc/bystar", icmsPkgName)
            varPath = os.path.join("/var/lib/bystar/", icmsPkgName)
            logPath = os.path.join("/var/log/bystar/", icmsPkgName)            
            tmpPath = os.path.join("/tmp/bystar", icmsPkgName)
            
        else:
            return icm.EH_critical_oops("basesPolicy={}".format(basesPolicy))

        pkgInfoParsSet().cmnd(
            interactive=False,
            icmsPkgInfoBaseDir=icmsPkgInfoBaseDir,
            icmsPkgBasesPolicy=basesPolicy,
            icmsPkgControlBaseDir=controlPath,
            icmsPkgVarBaseDir=varPath,
            icmsPkgLogBaseDir=logPath,            
            icmsPkgTmpBaseDir=tmpPath,
        )


    def cmndDesc(): """
** Set File Parameters at ../pkgInfo/fp -- By default
** TODO NOTYET auto detect marme.dev -- marme.control and decide where they should be, perhaps in /var/
"""
    

    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  pkgInfoParsDefaultsSetOLD    [[elisp:(org-cycle)][| ]]
"""
class pkgInfoParsDefaultsSetOLD(icm.Cmnd):
    """
** Set File Parameters at ../pkgInfo/fp -- By default
** TODO NOTYET auto detect marme.dev -- marme.control and decide where they should be, perhaps in /var/
"""

    cmndParamsMandatory = ['icmsPkgName']
    cmndParamsOptional = ['icmsPkgControlBaseDir', 'icmsPkgRunBaseDir']           
    cmndArgsLen = {'Min': 0, 'Max': 1,}
    cmndArgsSpec = {0: ['any']}    
    

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par "icmsPkgName icmsPkgControlBaseDir icmsPkgRunBaseDir" :args "basesPolicy"
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
        icmsPkgName=None,         # or Cmnd-Input
        icmsPkgControlBaseDir=None,         # or Cmnd-Input
        icmsPkgRunBaseDir=None,         # or Cmnd-Input
        basesPolicy=None,         # or Args-Input
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {'icmsPkgName': icmsPkgName, 'icmsPkgControlBaseDir': icmsPkgControlBaseDir, 'icmsPkgRunBaseDir': icmsPkgRunBaseDir, }
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
        icmsPkgName = callParamsDict['icmsPkgName']
        icmsPkgControlBaseDir = callParamsDict['icmsPkgControlBaseDir']
        icmsPkgRunBaseDir = callParamsDict['icmsPkgRunBaseDir']
####+END:
        G = icm.IcmGlobalContext()

        #basesPolicyChoices = self.__class__.cmndArgsSpec[0]

        if not basesPolicy:
            basesPolicy = G.icmRunArgsGet().cmndArgs[0]

        pkgInfoParsSet().cmnd(
            interactive=False,
            icmsPkgName=icmsPkgName,  
        )

        if basesPolicy == "bisosPolicy":
            return icm.EH_problem_usageError("basesPolicy={}".format(basesPolicy))
            
        elif basesPolicy == "bxoPolicy":
            if not icmsPkgControlBaseDir:
                return icm.EH_problem_usageError("")

            controlPath = icmsPkgControlBaseDir
            varPath = os.path.join(icmsRunEnvBaseDir_obtain(), "var", icmsPkgName_fpObtain())
            logPath = os.path.join(icmsRunEnvBaseDir_obtain(), "log", icmsPkgName_fpObtain())            
            tmpPath = os.path.join(icmsRunEnvBaseDir_obtain(), "tmp", icmsPkgName_fpObtain())

        elif basesPolicy == "runBaseDirPolicy":
            if not icmsPkgRunBaseDir:
                return icm.EH_problem_usageError("")
            
            if icmsPkgControlBaseDir:
                controlPath = icmsPkgControlBaseDir
            else:
                controlPath = os.path.join(icmsPkgRunBaseDir, "control", icmsPkgName_fpObtain())

            varPath = os.path.join(icmsPkgRunBaseDir, "var", icmsPkgName_fpObtain())
            logPath = os.path.join(icmsPkgRunBaseDir, "log", icmsPkgName_fpObtain())            
            tmpPath = os.path.join(icmsPkgRunBaseDir, "tmp", icmsPkgName_fpObtain())
            
        elif basesPolicy == "debianPolicy":
            controlPath = os.path.join("/etc/bystar", icmsPkgName)
            varPath = os.path.join("/var/lib/bystar/", icmsPkgName)
            logPath = os.path.join("/var/log/bystar/", icmsPkgName)            
            tmpPath = os.path.join("/tmp/bystar", icmsPkgName)
            
        elif basesPolicy == "centosPolicy":
            controlPath = os.path.join("/etc/bystar", icmsPkgName)
            varPath = os.path.join("/var/lib/bystar/", icmsPkgName)
            logPath = os.path.join("/var/log/bystar/", icmsPkgName)            
            tmpPath = os.path.join("/tmp/bystar", icmsPkgName)
            
        else:
            return icm.EH_critical_oops("basesPolicy={}".format(basesPolicy))

        pkgInfoParsSet().cmnd(
            interactive=False,
            icmsPkgBasesPolicy=basesPolicy,
            icmsPkgControlBaseDir=controlPath,
            icmsPkgVarBaseDir=varPath,
            icmsPkgLogBaseDir=logPath,            
            icmsPkgTmpBaseDir=tmpPath,
        )

        
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Run Envs Setup/Clean*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  icmsRunEnvsPreps    [[elisp:(org-cycle)][| ]]
"""
class icmsRunEnvsPreps(icm.Cmnd):
    """
** Create run time environment directories (tmp var)
"""
    cmndParamsMandatory = []
    cmndParamsOptional = []       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        #G = icm.IcmGlobalContext()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  icmsRunEnvsClean    [[elisp:(org-cycle)][| ]]
"""        
class icmsRunEnvsClean(icm.Cmnd):
    """
** Remove run time environment directories (tmp var)
    opDo rm -r "${icmsRunEnvBaseDir}/tmp/${icmsPkgName}"
    opDo rm -r "${icmsRunEnvBaseDir}/var/${icmsPkgName}"
"""
    cmndParamsMandatory = []
    cmndParamsOptional = []       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        #G = icm.IcmGlobalContext()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  icmsRunEnvLinks    [[elisp:(org-cycle)][| ]]
"""        
class icmsRunEnvLinks(icm.Cmnd):
    """
** Create links for ../tmp ../var and ../control
    opDo rm -r "${icmsRunEnvBaseDir}/tmp/${icmsPkgName}"
    opDo rm -r "${icmsRunEnvBaseDir}/var/${icmsPkgName}"
"""
    cmndParamsMandatory = []
    cmndParamsOptional = []       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        #G = icm.IcmGlobalContext()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  icmsRunEnvLinksClean    [[elisp:(org-cycle)][| ]]
"""        
class icmsRunEnvLinksClean(icm.Cmnd):
    """
** Remove links of ../tmp ../var and ../control
    opDo FN_fileSymlinkRemoveIfThere "${icmsPkgBaseDir}/tmp"
    opDo FN_fileSymlinkRemoveIfThere "${icmsPkgBaseDir}/var"

    opDo FN_fileSymlinkRemoveIfThere "${controlsBaseDir}"
"""
    cmndParamsMandatory = []
    cmndParamsOptional = []       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        #G = icm.IcmGlobalContext()
        
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  icmsLibsLinks    [[elisp:(org-cycle)][| ]]
"""        
class icmsLibsLinks(icm.Cmnd):
    """
** Creates links in ../lib/python/
    opDo FN_fileSymlinkUpdate /de/bx/nne/dev-py/libs/icmPkg/icm ${icmsPkgBaseDir}/lib/python/icm
    opDo FN_fileSymlinkUpdate /de/bx/nne/dev-py/libs/bxMsgPkg/bxMsg ${icmsPkgBaseDir}/lib/python/bxMsg
"""
    cmndParamsMandatory = []
    cmndParamsOptional = []       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        #G = icm.IcmGlobalContext()

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class-IIF    ::  icmsLibsLinksClean    [[elisp:(org-cycle)][| ]]
"""        
class icmsLibsLinksClean(icm.Cmnd):
    """
** Remove links in ../lib/python/
    opDo FN_fileSymlinkRemoveIfThere ${icmsPkgBaseDir}/lib/python/icm
    opDo FN_fileSymlinkRemoveIfThere ${icmsPkgBaseDir}/lib/python/bxMsg    
"""
    cmndParamsMandatory = []
    cmndParamsOptional = []       
    cmndArgsLen = {'Min': 0, 'Max': 0,}

####+BEGIN: bx:dblock:python:icm:cmnd:parsValidate :par ""
    @icm.subjectToTracking(fnLoc=True, fnEntry=True, fnExit=True)
    def cmnd(self,
        interactive=False,        # Can also be called non-interactively
    ):
        cmndOutcome = self.getOpOutcome()
        if interactive:
            if not self.cmndLineValidate(outcome=cmndOutcome):
                return cmndOutcome

        callParamsDict = {}
        if not icm.cmndCallParamsValidate(callParamsDict, interactive, outcome=cmndOutcome):
            return cmndOutcome
####+END:

        #G = icm.IcmGlobalContext()
        

####+BEGIN: bx:icm:python:section :title "End Of Editable Text"
"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(delete-other-windows)][(1)]]    *End Of Editable Text*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] 
"""
####+END:

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall
####+END:
