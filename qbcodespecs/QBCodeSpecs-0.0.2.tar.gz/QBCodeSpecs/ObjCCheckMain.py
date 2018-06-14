#!/usr/bin/env python
# -coding:utf-8
import sys
from QBCodeSpecs.antlr4 import *
from QBCodeSpecs.objcRecoginition.ObjectiveCLexer import *
from QBCodeSpecs.objcRecoginition.ObjectiveCParser import *
# from QBCodeSpecs.rules.custom.CustomClassNameRuleListener import *
# from QBCodeSpecs.rules.custom.CustomMethodNameRuleListener import *
from QBCodeSpecs.rules.name.ClassNameRuleListener import *
from QBCodeSpecs.rules.statements.SingletonRuleListener import *


from QBCodeSpecs.driver.ViolationDataMananger import *
from QBCodeSpecs.driver.Violation import *

from QBCodeSpecs.reporters.HTMLReporter import *

import json


import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class ObjCCheckMain(object):
    
    def load_config(self):
        with open("QBCodeSpecs/config/config.json",'r') as load_f:
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

    def check_file(self, inputstream, filepath):
        lexer = ObjectiveCLexer(inputstream)
        stream = CommonTokenStream(lexer)
        parser = ObjectiveCParser(stream)
        tree = parser.translationUnit()
        walker = ParseTreeWalker()

        # load rules
        rules = self.config['rules']
        # print rules


        # check class name
        classNameRules = rules["ClassName"]
        classNameRegex = classNameRules["Regex"]
        # print classNameRegex
        if len(classNameRegex) > 0:
            print "--------------------classNameRegex-------------------------"

            violation = Violation(filepath, classNameRules)
            # print violation
            classNameListener = ClassNameRuleListener(violation)
            # print classNameListener
            walker.walk(classNameListener, tree)
            # print walker

        print "--------------------singleton-------------------------"
        # singleton rule
        violation = Violation(filepath)
        singletonListener = SingletonRuleListener(violation)
        walker.walk(singletonListener, tree)

    def start_check(self):

        total_files = 0

        for filepath in self.filepathlist:

            if len(filepath) == 0:
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
            
        violationDataMananger.set_total_files_number(total_files)
        violationDataMananger.summary()
        # self.print_result()

        reporter = HTMLReporter()
        reporter.report('QBCodeToolsResult.html')

    
 
if __name__ == '__main__':
    
    # main(sys.argv)

    fileNamesString = sys.argv[1]

    base_path = ""
    if len(sys.argv) > 2:
        base_path = sys.argv[2]
    
    # print "fileNamesString--------"
    # print fileNamesString
    filenamelist = fileNamesString.split(';')
    checker = ObjCCheckMain(filepathlist=filenamelist, basepath=base_path)
    checker.start_check()
    
    # reporter = HTMLReporter()
    # reporter.report()
