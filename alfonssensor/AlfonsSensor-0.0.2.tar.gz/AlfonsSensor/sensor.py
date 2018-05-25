import threading
import time
import argparse
import imp
import os

import AlfonsIoT
import yaml

log = False

def thread(options):
	function = options["function"]
	topic = options["topic"]
	retain = options["retain"] if "retain" in options else False
	timeout = options["timeout"] if "timeout" in options else 5
	
	while True:
		data = getattr(script, function)()
		AlfonsIoT.mqtt.publish(topic, payload=data, qos=1, retain=retain)

		if log: print("Published %s to %s" % (data, topic))
		
		time.sleep(timeout)
	

def onConnect(*args):
	print("Connected")

	for t in config["topics"]:
		if not "function" in t or not "topic" in t:
			print("A sensor is missing a necessary field")
			continue
		
		threading.Thread(target=thread, args=(t, )).start()

def run():
	global config, script, log

	parser = argparse.ArgumentParser()
	parser.add_argument("config_file", help="Path for the config file")
	parser.add_argument("-p", action="store_true", help="Print every publish. Good for testing", dest="print")
	args = parser.parse_args()
	
	log = args.print

	configPath = os.path.abspath(args.config_file)
	config = {}

	with open(configPath) as f:
		config = yaml.load(f)

	scriptPath = os.path.abspath(os.path.dirname(configPath) + "/" + config["script"])
	script = imp.load_source("Alfons Sensor", scriptPath)

	AlfonsIoT.connect(on_connect=onConnect, block=True)