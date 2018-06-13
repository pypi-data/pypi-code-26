# -*- coding: utf-8 -*-
"""
Caissa voice-controlled personal assistant
Copyright © 2018  Dieter Dobbelaere

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from .brain import Brain
from .sense import Sense
from .skills import Skill
from .speech import Speech
from .hearing import *


class Caissa:
    """
    Caissa voice-controlled personal assistant
    """
    
    def __init__(self):
        """
        Construct and connect Caissa's vital organs
        """
        
        # initialize senses
        sense = Sense()
        speech = Speech()
        
        # initialize brain
        self.brain = Brain(hearing=None, sense=sense, speech=speech)
    
    def live_forever(self):
        """
        Bring Caissa to life
        """
        
        self.brain.think_forever()
