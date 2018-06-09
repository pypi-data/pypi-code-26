import os

def exec_sys_cmd(sys_cmd):
  sp = subprocess.Popen(sys_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  out, err = sp.communicate()
  return (out.decode('utf-8'), err.decode('utf-8'))