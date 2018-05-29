# -*- coding: utf-8 -*-
from A1_41 import corrector as ap

atrs = []
while ap.__name__ not in ['object', 'Message', 'MessageMase']:
    atrs += ap.__dict__.keys()
    ap = ap.__base__
out = open("tout.txt", 'w')
txt = "self.assertEqual({0}.{1}, '')\n"
name = 'corrector'

xmlatrs = u"""<reqcode>
<comreferencenum>
<responsedate>
<responsehour>
<nationality>
<documenttype>
<documentnum>
<cups>
<atrcode>
<transfereffectivedate>
<telemetering>
<finalqdgranted>
<finalqhgranted>
<finalclientyearlyconsumption>
<gasusetype>
<updatereason>
<result>
<resultdesc>
<activationtype>
<activationtypedesc>
<closingtype>
<closingtypedesc>
<interventiondate>
<interventionhourfrom>
<interventionhourto>
<visitnumber>
<firstname>
<familyname1>
<familyname2>
<titulartype>
<regularaddress>
<telephone1>
<telephone2>
<email>
<language>
<provinceowner>
<cityowner>
<zipcodeowner>
<streettypeowner>
<streetowner>
<streetnumberowner>
<portalowner>
<staircaseowner>
<floorowner>
<doorowner>
<canonircperiodicity>
<lastinspectionsdate>
<lastinspectionsresult>
<StatusPS>
<readingtype>
<lectureperiodicity>
<extrainfo>
<counterlist>
<counter>
<countermodel>
<countertype>
<counternumber>
<counterproperty>
<reallecture>
<counterpressure>
<correctorlist>
<corrector>
<correctormodel>
<correctortype>
<correctornumber>
<correctorproperty>
<correctedlecture>
"""


for art in sorted([a for a in atrs if a[0] != '_']):
    if art in xmlatrs:
        out.write(txt.format(name, art))
