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


def ssh_remote_host(ssh_cmd, remote_user, remote_host, remote_cmd)  
  local_cmd  =  [ssh_cmd , remote_user + '@' + remote_host, remote_cmd ]
  output,error = exec_sys_cmd(local_cmd)
  
    
def boot_remote_host(wol_cmd, local_nic, remote_host, remote_host_mac):
  boot_cmd    = [wol_cmd, '-i', local_nic , remote_host_mac] 
  me.exec_sys_cmd(boot_cmd)
  for i in range (int(me.config['REMOTE_BOOT_MAX_TIME'])):
    time.sleep(1)
    output,error = me.exec_sys_cmd(detect_cmd)
    me.write_log(log_file, '[' + me.config['REMOTE_HOST'] + '] : ' + output + error)
    if me.config['REMOTE_HOST'] in output: 
      me.write_log(log_file, 'Remote Host Started :' + me.config['REMOTE_HOST'])
      return
   


def shut_remote():   
  me.write_log(log_file,'Shutdown Remote Host') 
  shut_cmd  =  [me.config['LOCAL_SSH_CMD'], me.config['REMOTE_ROOT'] + '@' + me.config['REMOTE_HOST'],'shutdown -h now']
  output,error = me.exec_sys_cmd(shut_cmd)
  me.write_log(log_file, '[' + me.config['REMOTE_HOST'] + '] : ' + output + error)
  
  
if __name__ == "__main__":
 
  pass  