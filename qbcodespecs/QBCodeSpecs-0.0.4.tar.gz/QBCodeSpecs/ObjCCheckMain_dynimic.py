#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.antlr4 import *
from QBCodeSpecs.objcRecoginition.ObjectiveCLexer import *
from QBCodeSpecs.objcRecoginition.ObjectiveCParser import *

from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *

from QBCodeSpecs.reporters.HTMLReporter import *
import QBCodeSpecs
import json
import os
import re
import click

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ObjCCheckMain(object):
    
    def load_config(self):
        configPath = "config/config.json"
        path = os.path.dirname(QBCodeSpecs.__file__)
        exploit_path=os.path.join(path,configPath)
        # sys.path.append(exploit_path)

        with open(exploit_path,'r') as load_f:
            load_dict = json.load(load_f)
            self.config = load_dict
        
            # print load_dict


    # def __init__(self, filepathStr = ""):
    #     super(ObjCCheckMain, self).__init__()
    #     filepathlist = filepathStr.split(';')
    #     self.filepathlist = filepathlist
    #     self.load_config()
    #     print len(self.filepathlist)


    def __init__(self, filepathlist = [], basepath = ""):
       
        super(ObjCCheckMain, self).__init__()
        self.filepathlist = filepathlist
        self.basepath = basepath
        self.config = {}
        self.load_config()
        # print len(self.filepathlist)


#def walkerTree(stream, listener):
#    parser = ObjectiveCParser(stream)
#    tree = parser.translationUnit()
#    walker = ParseTreeWalker()
#    walker.walk(listener, tree)
    # print("LISP:")
    # print(tree.toStringTree(parser))
             
    def print_result(self):
        print "final results:--------------------------------"

        violations = violationDataMananger.list
        for x in violations:
            if isinstance(x, Violation):
                info = "filepath:" + x.path + " " + "line number:" + str(x.startline) + " "+ "columnNum:" + str(x.startcolumn) + " " + "Message:" + x.message + " " + "DemoCode:" + x.get_democode()
                print info
        return len(violations)

    def is_valid_rule(self, ruleclassname):
        
        rulename = self.ruleNameFormClassName(ruleclassname)
        
        if self.config.has_key('invalidRules'):

            invalidRules = self.config['invalidRules']
            if rulename in invalidRules:
                return False
        
        return True

    def ruleNameFormClassName(self, ruleclassname):
        if ruleclassname.endswith('RuleListener') == False:
            return ""

        rulenamelen = len(ruleclassname) - len('RuleListener')
        if rulenamelen == 0:
            return ""

        rulename = ruleclassname[0:rulenamelen]
        return rulename

    def valid_rule_listener_class(self):
        # key: className value: Class
        valid_class = {}

        validDir = ["name", "statements", "custom"]
        for rulesDir in validDir:
            rulepath = "rules/" + rulesDir

            # path=os.path.abspath('.')
            # print "path --" + path
            # print  sys.modules['QBCodeSpecs']
            path = os.path.dirname(QBCodeSpecs.__file__)
            # print path
            exploit_path=os.path.join(path,rulepath)
            sys.path.append(exploit_path)

            modules=[x for x in os.listdir(exploit_path) if os.path.isfile(os.path.join(exploit_path,x)) and os.path.splitext(x)[1]=='.py']
            for m in modules:
                if m!='__init__.py':
                    module_name=os.path.join(exploit_path,os.path.splitext(m)[0])
                    class_name = os.path.splitext(m)[0]
                    # print module_name
                    # print "[0]:" + class_name

                    if self.is_valid_rule(class_name) :
                        module=__import__(os.path.splitext(m)[0])
                        ruleLinstenerCls=getattr(module,class_name)
                        # print self.ruleNameFormClassName(class_name)
                        # print ruleLinstenerCls
                        valid_class[self.ruleNameFormClassName(class_name)] = ruleLinstenerCls
             

        # print valid_class
        return valid_class


    def check_file(self, inputstream, filepath):

        lexer = ObjectiveCLexer(inputstream)
        stream = CommonTokenStream(lexer)
        parser = ObjectiveCParser(stream)
        tree = parser.translationUnit()
        walker = ParseTreeWalker()

        # load rules
        rules = {}
        if self.config.has_key('rules'):
            rules = self.config['rules']
        
        # print rules
        
        listenerClassDict = self.valid_rule_listener_class()
        for (k,v) in  listenerClassDict.items(): 
            rulename = k
            listenerCls = v

            violation = None
            # has dict para
            if rules.has_key(rulename) :
                para = rules[rulename]
                violation = Violation(filepath, para)
            else:
                violation = Violation(filepath)
            listener = listenerCls(violation)
            walker.walk(listener, tree)


    def isIgnorePath(self, path):
        if len(path) == 0:
            return True

        if self.config.has_key('ignorePath') :
            ignorePath = self.config['ignorePath']
            for iPathRegex in ignorePath:
                # print "-----iPathRegex:" + iPathRegex
                # print "path:" + path
                if re.match(iPathRegex, path) :
                    return True
        return False

    def start_check(self):

        total_files = 0

        for filepath in self.filepathlist:

            if self.isIgnorePath(filepath) :
                continue

            absolute_path = ""
            if len(self.basepath) > 0:
                absolute_path = self.basepath + "/" + filepath
            else:
                absolute_path = filepath


            inputstream = None
            try:
                inputstream = FileStream(absolute_path, encoding='utf-8')
                # input = FileStream(filepath)
                print "open file--------------------------------"
                print "filepath:" + filepath
            except IOError:
                print "IOError**********************************"
                print "basepath:" + self.basepath
                print "filepath:" + filepath
                continue
            else:
                pass
            finally:
                pass

            if input == None:
                continue
            # print input

            # record total_files
            total_files = total_files + 1
            self.check_file(inputstream, absolute_path)
            
        if total_files == 0 :
            print "--------------no error---------------"
            return
        else :
            print "--------------check end---------------"
        violationDataMananger.set_total_files_number(total_files)
        violationDataMananger.summary()
        # self.print_result()

        reporter = HTMLReporter()
        reporter.report('QBCodeToolsResult.html')

        error_num = len(violationDataMananger.list)
        return error_num
        
        # print "return info: " + str(len(violationDataMananger.list))
        # return len(violationDataMananger.list)

@click.command()
@click.option('-c', '--config', default=None, help='Config file path')
def enter(config):
    if argv is None:
        argv = sys.argv

    if len(argv) < 2:
        return 0
          
    fileNamesString = argv[1]
    base_path = ""
    # if len(argv) > 2:
    #     base_path = argv[2]
    
    # print "fileNamesString--------"
    # print fileNamesString
    filenamelist = fileNamesString.split(';')
    checker = ObjCCheckMain(filepathlist=filenamelist, basepath=base_path)
    error_num = checker.start_check()
    # if error_num > 0:
    #     return 1
    # else:
    #     return 0
    if error_num > 0:
        return sys.exit(1)
    else:
        return sys.exit(0)


# def main(argv=None):
#     # fileNamesString = sys.argv[1]
#     if argv is None:
#         argv = sys.argv

#     if len(argv) < 2:
#         return 0
          
#     fileNamesString = argv[1]
#     base_path = ""
#     if len(argv) > 2:
#         base_path = argv[2]
    
#     # print "fileNamesString--------"
#     # print fileNamesString
#     filenamelist = fileNamesString.split(';')
#     checker = ObjCCheckMain(filepathlist=filenamelist, basepath=base_path)
#     error_num = checker.start_check()
#     # if error_num > 0:
#     #     return 1
#     # else:
#     #     return 0
#     if error_num > 0:
#         return sys.exit(1)
#     else:
#         return sys.exit(0)


if __name__ == '__main__':
    # main()
    enter()
    # sys.exit(main())
