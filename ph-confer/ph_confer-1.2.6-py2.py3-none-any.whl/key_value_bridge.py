from threading import Thread

from etcd import EtcdWatchTimedOut
from etcd.client import Client as ETCDClient
from ph_confer.within_template_config import confer_instance

try:
  from queue import Queue, Empty
except ImportError:
  from Queue import Queue, Empty


class TemplateApi:
  def __init__(
      self,
      watch_timeout,
      auto_add_watches,
      endpoints,
      use_ssl,
      client_key,
      client_cert,
      ca_cert
  ):
    if endpoints is None:
      endpoints = [('localhost', 2379)]
    if bool(client_cert) != bool(client_key):
      raise Exception(
          'Both client cert and key need to be specified to use either.'
      )
    self.etcd_cli_kwargs = {
      'host': endpoints,
      'protocol': 'https' if use_ssl else 'http',
      'allow_reconnect': True
    }
    if client_cert:
      self.etcd_cli_kwargs['cert'] = (client_cert, client_key)
    if ca_cert:
      self.etcd_cli_kwargs['ca_cert'] = ca_cert
    self.watch_timeout = watch_timeout
    self.auto_add_watches = auto_add_watches

  def get_key(self, key):
    if self.auto_add_watches:
      confer_instance.watched_keys.append(key)
    return ETCDClient(**self.etcd_cli_kwargs).get(key).value

  def get_key_values_in_dir(self, d):
    if self.auto_add_watches:
      confer_instance.watched_keys.append(d)
    ret = {}
    for f in ETCDClient(**self.etcd_cli_kwargs).get(d).children:
      k = f.key[len(d):].strip('/')
      if k:
        ret[k] = f.value
    return ret.items()

  def get_keys_in_dir(self, d):
    if self.auto_add_watches:
      confer_instance.watched_keys.append(d)
    ret = set()
    for f in ETCDClient(**self.etcd_cli_kwargs).get(d).children:
      k = f.key[len(d):].strip('/')
      if k:
        ret.add(k)
    return ret

  def get_values_in_dir(self, d):
    if self.auto_add_watches:
      confer_instance.watched_keys.append(d)
    ret = []
    for f in ETCDClient(**self.etcd_cli_kwargs).get(d).children:
      ret.append(f.value)
    return ret

  def watch_keys(self, keys):
    print('Watching keys {}'.format(keys))
    q = Queue()

    def watch_and_notify(key):
      try:
        ETCDClient(**self.etcd_cli_kwargs).watch(key, timeout=self.watch_timeout, recursive=True)
      except EtcdWatchTimedOut:
        pass
      q.put(True)

    for key in keys:
      t = Thread(target=watch_and_notify, args=(key,))
      t.daemon = True
      t.start()
    try:
      q.get(block=True, timeout=self.watch_timeout)
    except Empty:
      pass


_instance = None


def get_key_values_in_dir(d):
  return _instance.get_key_values_in_dir(d)


def get_keys_in_dir(d):
  return _instance.get_keys_in_dir(d)


def get_values_in_dir(d):
  return _instance.get_values_in_dir(d)


def get_key(key):
  return _instance.get_key(key)


def watch_keys(keys):
  return _instance.watch_keys(keys)


def setinstance(
    watch_timeout=60,
    auto_add_watches=True,
    endpoints=None,
    use_ssl=False,
    client_key=None,
    client_cert=None,
    ca_cert=None
):
  global _instance
  _instance = TemplateApi(
      watch_timeout=watch_timeout,
      auto_add_watches=auto_add_watches,
      endpoints=endpoints,
      use_ssl=use_ssl,
      client_key=client_key,
      client_cert=client_cert,
      ca_cert=ca_cert
  )
