import os
import sys
def notify(title, text):
	if sys.platform[:3] == 'dar':
		os.popen("""
			osascript -e 'display notification "{}" with title "{}"'
        	""".format(text, title))
		
