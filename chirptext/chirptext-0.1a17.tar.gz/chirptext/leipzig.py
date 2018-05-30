# -*- coding: utf-8 -*-

'''
Leipzig standard abbreviations

Latest version can be found at https://github.com/letuananh/chirptext

References:
    The Leipzig Glossing Rules
        https://www.eva.mpg.de/lingua/pdf/Glossing-Rules.pdf

:copyright: (c) 2012 Le Tuan Anh <tuananh.ke@gmail.com>
:license: MIT, see LICENSE for more details.
'''

import logging

from .anhxa import DataObject


# -------------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------------

def getLogger():
    return logging.getLogger(__name__)


# -------------------------------------------------------------------------------
# Data Structures
# -------------------------------------------------------------------------------

class SmartTag(DataObject):

    def __init__(self, label, description='', **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.description = description

    def __repr__(self):
        return "SmartTag(label={})".format(repr(self.label))

    def __str__(self):
        return str(self.label) if self.label is not None else ''


# Adopted from version: Leipzig, last change: May 31, 2015
# Name changed:
#    + 1, 2, 3 -> _1, _2, _3
#    + N- -> NON
_1 = SmartTag('1', 'first person')
_2 = SmartTag('2', 'second person')
_3 = SmartTag('3', 'third person')
A = SmartTag('A', 'agent-like argument of canonical transitive verb')
ABL = SmartTag('ABL', 'ablative')
ABS = SmartTag('ABS', 'absolutive')
ACC = SmartTag('ACC', 'accusative')
ADJ = SmartTag('ADJ', 'adjective')
ADV = SmartTag('ADV', 'adverb(ial)')
AGR = SmartTag('AGR', 'agreement')
ALL = SmartTag('ALL', 'allative')
ANTIP = SmartTag('ANTIP', 'antipassive')
APPL = SmartTag('APPL', 'applicative')
ART = SmartTag('ART', 'article')
AUX = SmartTag('AUX', 'auxiliary')
BEN = SmartTag('BEN', 'benefactive')
CAUS = SmartTag('CAUS', 'causative')
CLF = SmartTag('CLF', 'classifier')
COM = SmartTag('COM', 'comitative')
COMP = SmartTag('COMP', 'complementizer')
COMPL = SmartTag('COMPL', 'completive')
COND = SmartTag('COND', 'conditional')
COP = SmartTag('COP', 'copula')
CVB = SmartTag('CVB', 'converb')
DAT = SmartTag('DAT', 'dative')
DECL = SmartTag('DECL', 'declarative')
DEF = SmartTag('DEF', 'definite')
DEM = SmartTag('DEM', 'demonstrative')
DET = SmartTag('DET', 'determiner')
DIST = SmartTag('DIST', 'distal')
DISTR = SmartTag('DISTR', 'distributive')
DU = SmartTag('DU', 'dual')
DUR = SmartTag('DUR', 'durative')
ERG = SmartTag('ERG', 'ergative')
EXCL = SmartTag('EXCL', 'exclusive')
F = SmartTag('F', 'feminine')
FOC = SmartTag('FOC', 'focus')
FUT = SmartTag('FUT', 'future')
GEN = SmartTag('GEN', 'genitive')
IMP = SmartTag('IMP', 'imperative')
INCL = SmartTag('INCL', 'inclusive')
IND = SmartTag('IND', 'indicative')
INDF = SmartTag('INDF', 'indefinite')
INF = SmartTag('INF', 'infinitive')
INS = SmartTag('INS', 'instrumental')
INTR = SmartTag('INTR', 'intransitive')
IPFV = SmartTag('IPFV', 'imperfective')
IRR = SmartTag('IRR', 'irrealis')
LOC = SmartTag('LOC', 'locative')
M = SmartTag('M', 'masculine')
N = SmartTag('N', 'neuter')
NON = SmartTag('N-', 'non- (e.g. NSG nonsingular, NPST nonpast)')
NEG = SmartTag('NEG', 'negation, negative')
NMLZ = SmartTag('NMLZ', 'nominalizer/nominalization')
NOM = SmartTag('NOM', 'nominative')
OBJ = SmartTag('OBJ', 'object')
OBL = SmartTag('OBL', 'oblique')
P = SmartTag('P', 'patient-like argument of canonical transitive verb')
PASS = SmartTag('PASS', 'passive')
PFV = SmartTag('PFV', 'perfective')
PL = SmartTag('PL', 'plural')
POSS = SmartTag('POSS', 'possessive')
PRED = SmartTag('PRED', 'predicative')
PRF = SmartTag('PRF', 'perfect')
PRS = SmartTag('PRS', 'present')
PROG = SmartTag('PROG', 'progressive')
PROH = SmartTag('PROH', 'prohibitive')
PROX = SmartTag('PROX', 'proximal/proximate')
PST = SmartTag('PST', 'past')
PTCP = SmartTag('PTCP', 'participle')
PURP = SmartTag('PURP', 'purposive')
Q = SmartTag('Q', 'question particle/marker')
QUOT = SmartTag('QUOT', 'quotative')
RECP = SmartTag('RECP', 'reciprocal')
REFL = SmartTag('REFL', 'reflexive')
REL = SmartTag('REL', 'relative')
RES = SmartTag('RES', 'resultative')
S = SmartTag('S', 'single argument of canonical intransitive verb')
SBJ = SmartTag('SBJ', 'subject')
SBJV = SmartTag('SBJV', 'subjunctive')
SG = SmartTag('SG', 'singular')
TOP = SmartTag('TOP', 'topic')
TR = SmartTag('TR', 'transitive')
VOC = SmartTag('VOC', 'vocative')
