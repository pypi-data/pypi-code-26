
import wdisp
import argparse
import time

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Image Server')
    parser.add_argument('--port', help = "Server port")
    args = parser.parse_args()
        
    wdisp.run_server_process(port = args.port)
    print("Server listening on", wdisp.config.root_url())
    print("Press Ctrl-C to stop program")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        pass

