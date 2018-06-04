import os
import socket
import sys
import http.server
import socketserver


def test_port (host, port):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((host,port))
  if result == 0: 
    return True # open
  return False

def http_server(port, web_path) :
  os.chdir(web_path)
  Handler = http.server.SimpleHTTPRequestHandler
  httpd = socketserver.TCPServer(("", port), Handler)
  print("HTTP Server started at port : ", port)
  try:
    httpd.serve_forever()
  except KeyboardInterrupt:
    httpd.shutdown()
    sys.exit(0)
  sys.exit(0)  
  
if __name__ == "__main__":
 
  pass  