
import time
import arrow

from django.core.management.base import BaseCommand, CommandError

class ThrottleMixinCommand(object):
    LONG_THROTTLE = 1
    SHORT_THROTTLE = 0.1
    THROTTLE_THRESHOLD = None

    def _throttle_network(self):
        if self.THROTTLE_THRESHOLD == None:
            return
        
        if hasattr(self, '_throttle') == False:
            self._throttle = 0

        else:
            self._throttle += 1
            if self._throttle == 10:
                time.sleep(self.LONG_THROTTLE)
                self._throttle = 0
            
            else:
                time.sleep(self.SHORT_THROTTLE)

