#==============================================================================
# Copyright 2018 Marco Bellaccini - marco.bellaccini[at!]gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#==============================================================================

# test suite for templatio

import unittest
import textfsm
from jinja2 import Template, exceptions
from io import StringIO
import templatio


# conversion tests
class TestConversion(unittest.TestCase):
    # test simple, successful, conversion
    def test_simple_conv_ok(self):
        
        intempl = ("Value Name (\S+)\n"
                   "Value Surname (\S+)\n"
                   "\n"
                   "Start\n"
                   "  ^Name: ${Name}\n"
                   "  ^Surname: ${Surname}\n")

        
        outtempl = ("Name is {{ Name }}\n"
                    "Surname is {{ Surname }}")
        
        inData = ("Name: John\n"
                  "Surname: Doe")
        
        expOut = ("Name is John\n"
                  "Surname is Doe")
        
        self.assertEqual(templatio.parseInToOut(intempl, outtempl, inData), 
                         expOut)
        
    # test no match w.r.t. input template
    def test_nomatch_in(self):
        
        intempl = ("Value Name (\S+)\n"
                   "Value Surname (\S+)\n"
                   "\n"
                   "Start\n"
                   "  ^Name: ${Name}\n"
                   "  ^Surname: ${Surname}\n")

        
        outtempl = ("Name is {{ Name }}\n"
                    "Surname is {{ Surname }}")
        
        inData = ("Foo123")
        
        expOut = ("Name is \n"
                  "Surname is ")
        
        self.assertEqual(templatio.parseInToOut(intempl, outtempl, inData), 
                         expOut)
        
    # test partial match w.r.t. input template
    def test_partmatch_in(self):
        
        intempl = ("Value Name (\S+)\n"
                   "Value Surname (\S+)\n"
                   "\n"
                   "Start\n"
                   "  ^Name: ${Name}\n"
                   "  ^Surname: ${Surname}\n")

        
        outtempl = ("Name is {{ Name }}\n"
                    "Surname is {{ Surname }}")
        
        inData = ("Foo123\n"
                  "Surname: Doe")
        
        expOut = ("Name is \n"
                  "Surname is Doe")
        
        self.assertEqual(templatio.parseInToOut(intempl, outtempl, inData), 
                         expOut)
        
# template tests
class TestTemplate(unittest.TestCase):
    # test bad input template
    def test_bad_in_template(self):
        
        intempl = ("FooBaz")
        
        outtempl = ("Name is {{ Name }}\n"
                    "Surname is {{ Surname }}")
        
        inData = ("Name: John\n"
                  "Surname: Doe")
        
        # get exception message from TextFSM
        exm = str()
        try:
            textfsm.TextFSM(StringIO(intempl))
        except textfsm.TextFSMTemplateError as tmpex:
            exm = str(tmpex)
        
        self.assertRaisesRegex(ValueError,
                               ("Error: invalid input template.\n" + exm ),
                               templatio.parseInToOut, intempl,
                               outtempl, inData)
        
    # test bad output template
    def test_bad_out_template(self):
        
        intempl = ("Value Name (\S+)\n"
                   "Value Surname (\S+)\n"
                   "\n"
                   "Start\n"
                   "  ^Name: ${Name}\n"
                   "  ^Surname: ${Surname}\n")
        
        outtempl = ("Name is {{ Name }}\n"
                    "Surname is {{ }}")
        
        inData = ("Name: John\n"
                  "Surname: Doe")
        
        # get exception message from Jinja2
        exm = str()
        try:
            Template(outtempl)
        except exceptions.TemplateSyntaxError as tmpex:
            exm = str(tmpex)
        
        self.assertRaisesRegex(ValueError,
                               ("Error: invalid output template.\n" + exm ),
                               templatio.parseInToOut, intempl,
                               outtempl, inData)
        

if __name__ == '__main__':
    unittest.main()
