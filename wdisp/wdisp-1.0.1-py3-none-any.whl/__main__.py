
import wdisp
import argparse

parser = argparse.ArgumentParser(description='Image Server')
parser.add_argument('--port', help = "Server port")
args = parser.parse_args()
	
wdisp.run_server(port = args.port)


