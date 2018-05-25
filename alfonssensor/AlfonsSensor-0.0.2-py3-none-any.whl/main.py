import AlfonsIoT
import argparse
import imp
import threading
import time

def thread(options):
	function = options["function"]
	topic = options["topic"]
	retain = options["retain"] if "retain" in options else False
	timeout = options["timeout"] if "timeout" in options else 5
	
	while True:
		data = getattr(script, function)()
		AlfonsIoT.mqtt.publish(topic, payload=data, qos=1, retain=retain)
		time.sleep(timeout)
	

def onConnect(*args):
	print("Connected")

	for t in config["topics"]:
		if not "function" in t or not "topic" in t:
			print("A sensor is missing a necessary field")
			continue
		
		threading.Thread(target=thread, args=(t, )).start()

def main():
	global config
	global script
	
	parser = argparse.ArgumentParser()
	parser.add_argument("config_file", help="Path for the config file")
	args = parser.parse_args()

	configPath = AlfonsIoT.os.path.abspath(args.config_file)
	config = {}

	with open(configPath) as f:
		config = AlfonsIoT.yaml.load(f)

	scriptPath = AlfonsIoT.os.path.abspath(AlfonsIoT.os.path.dirname(configPath) + "/" + config["script"])
	script = imp.load_source("Alfons Sensor", scriptPath)
	
	AlfonsIoT.connect(on_connect=onConnect, block=True)