#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
FILE:
  notification/main.py

NAME:
  notification.main

DESCRIPTION:
  Notification related functionalities

USAGE:
  ```
  import notification.main as notification
  notification.send('<Message>', '<Title>')
  ```

'''
__version__     = 1.0
__author__      = "Richard Li"

from osascript import osascript

# send message with title as notification
def send(message, title):
  '''
  :param message: message will be sent
  :param title: title will be sent with message
  '''
  returncode,stdout,stderr = osascript('display notification "{message}" with title "{title}"'.format(message=message, title=title))


# module entry
if __name__ == '__main__':
  send('Hi Message', 'Mr, Title')