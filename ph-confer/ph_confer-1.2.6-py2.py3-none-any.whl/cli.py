import argparse
import time
import traceback
import os

import sys

from ph_confer import key_value_bridge
from ph_confer import template_manager
from ph_confer.within_template_config import confer_instance
from ph_confer.exceptions import ConfigException


def template_walk(files):
  ret = set()
  for f in files:
    if os.path.isdir(f):
      for filename in os.listdir(f):
        ret.add(os.path.join(f, filename))
    elif os.path.exists(f):
      ret.add(f)
    else:
      raise Exception("Template file or directory {} doesn't exist.".format(f))
  return ret


def main():
  main_parser = argparse.ArgumentParser(description='PH Confer')
  main_parser.add_argument('templates', nargs='*', default=['/etc/ph_confer/'])
  main_parser.add_argument('--onetime', action='store_true')
  main_parser.add_argument('--auto-add-watches', action='store_false')
  main_parser.add_argument('--watch-period', type=int, default=60)
  main_parser.add_argument(
      '--kv-endpoints', type=str, default='localhost:2379,localhost:2380'
  )
  main_parser.add_argument('--kv-ssl', action='store_true')
  main_parser.add_argument('--kv-client-key')
  main_parser.add_argument('--kv-client-cert')
  main_parser.add_argument('--kv-ca-cert')

  args = main_parser.parse_args()
  endpoints = tuple([
    (s.split(':', 1)[0], int(s.split(':')[1]))
    for s in args.kv_endpoints.split(',')
  ])
  while True:
    failed = False
    all_listen_keys = set()
    for d in template_walk(args.templates):
      print('Rendering template {}...'.format(d))
      try:
        key_value_bridge.setinstance(
            watch_timeout=args.watch_period,
            auto_add_watches=args.auto_add_watches,
            endpoints=endpoints,
            use_ssl=args.kv_ssl,
            client_key=args.kv_client_key,
            client_cert=args.kv_client_cert,
            ca_cert=args.kv_ca_cert
        )
        template_changed = template_manager.run_template(d)
        if template_changed:
          print('Template {} changed.'.format(d))
      except ConfigException:
        failed = True
        traceback.print_exc()
      all_listen_keys.update(confer_instance.watched_keys)
    if args.onetime:
      sys.exit(1 if failed else 0)
    print('Waiting for {} seconds or for a watched key to change.'
      .format(args.watch_period))
    if all_listen_keys:
      key_value_bridge.watch_keys(all_listen_keys)
    else:
      time.sleep(args.watch_period)
