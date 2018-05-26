import requests, datetime, textwrap, urllib.request
from bs4 import BeautifulSoup
from huepy import *

class Way2sms(object):
    URL = 'http://www.way2sms.com'

    def __init__(self):
        self.base_url = requests.head(Way2sms.URL, allow_redirects=True).url  # url after redirect
        self.session = requests.session()
        self.token = ''

    def login(self, username, password):
        self.session.headers.update({'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Cache-Control': 'no-cache',
                                     'Upgrade-Insecure-Requests': '1',
                                     'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
                                     'Content-Type': 'application/x-www-form-urlencoded',
                                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                     'DNT': '1', 'Accept-Encoding': 'gzip, deflate',
                                     'Accept-Language': 'en-US,en;q=0.8'})

        payload = {
            'username': username,
            'password': password
        }
        if len(payload['username']) == 10:
        	_login_url = '/'.join([self.base_url, 'Login1.action?'])
        	_login = self.session.post(_login_url, data=payload)

        	if _login.ok:
        		self.token = self.session.cookies['JSESSIONID']
        		self.token = self.token[4:]
        		print(run(white('Processing...')))
        		print(good(lightgreen('Successfully logged in.')))
        	else:
        		print(bad(red('Login failed')))
        else:
        	print(bad(red('Please Enter Correct Username.')))

    def logout(self):
        _logout_url = '/'.join([self.base_url, 'main.action'])
        self.session.get(_logout_url)
        self.token = ''
        self.session.close()
        print(run(white('Processing...')))
        print(good(lightgreen('Successfully logged out')))

    def send(self, to_number, message):

        if not self.token:
            print(bad(red('Not logged in')))
            return

        _send_sms_url = '/'.join([self.base_url, 'smstoss.action'])

        url_safe_message = message.strip()

        message_list = textwrap.wrap(url_safe_message, 140)

        for i, message in enumerate(message_list):
            message_length = len(message)

            payload = {
                'ssaction': 'ss',
                'Token': self.token,
                'mobile': to_number,
                'message': message,
                'msgLen': str(140 - message_length)
            }

            resp = self.session.post(_send_sms_url, data=payload)

            quota_finished_text = "Rejected : Can't submit your message, finished your day quota."

            if len(message_list) > 1:
                print('Part [{}/{}]'.format(i + 1, len(message_list)), end=' ')

            if quota_finished_text not in resp.text:
                if self._sent_verify(to_number, message):
                    print(good(lightgreen('Successfully sent.')))
                else:
                    print(bad(red('Failed to send.')))
            else:
                print(bad(red('Not sent, Quota finished.')))

    def _sent_verify(self, mobile, message):
        print(info(white('Verifying sent message...')))
        if not self.token:
            print(bad(red('Not logged in')))
            return

        today = datetime.date.today().strftime('%d/%m/%Y')

        payload = {
            'Token': self.token,
            'dt': today
        }

        _sent_verify_url = '/'.join([self.base_url, 'sentSMS.action'])

        resp = self.session.post(_sent_verify_url, data=payload)

        soup = BeautifulSoup(resp.text, 'html.parser')

        first = soup.find('div', {'class': 'mess'})
        _mobile = str(first.find('b').text)
        divrb = first.find('div', {'class': 'rb'})
        _message = str(divrb.find('p').text)
        if _mobile == str(mobile) and _message == message:
            return True
        else:
            return False

    def schedule(self, mobile, message, date, time):
        if not self.token:
            print(bad(red('Not logged in')))
            return

        _schedule_url = '/'.join([self.base_url, 'schedulesms.action'])

        _date = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%d/%m/%Y')
        _time = datetime.datetime.strptime(time, '%H:%M').strftime('%H:%M')

        url_safe_message = message.strip()

        message_list = textwrap.wrap(url_safe_message, 140)

        quota_finished_text = "Rejected : Can't submit your message, finished your day quota."

        for i, message in enumerate(message_list):
            message_length = len(message)

            payload = {
                'Token': self.token,
                'mobile': mobile,
                'sdate': _date,
                'stime': _time,
                'message': message,
                'msgLen': str(140 - message_length)
            }

            resp = self.session.post(_schedule_url, data=payload)

            if len(message_list) > 1:
                print('Part [{}/{}]'.format(i + 1, len(message_list)), end=' ')

            if quota_finished_text not in resp.text:
                if self._schedule_verify(mobile, message, date, time):
                    print(good(lightgreen('Successfully scheduled, on {} {}'.format(_date, _time))))
                else:
                    print(bad(red('Unable to schedule message.')))
            else:
                print(bad(red('Not sent, Quota finished.')))

    def _schedule_verify(self, mobile, message, date, time):
        print(info(white('Verifying scheduled message...')))
        if not self.token:
            print(bad(red('Not logged in')))
            return

        _date = datetime.datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
        _time = datetime.datetime.strptime(time, '%H:%M').strftime('%I:%M %p')

        timestamp = '{} {}'.format(_time, _date)

        payload = {
            'Token': self.token,
            'dt': _date
        }

        _sent_verify_url = '/'.join([self.base_url, 'MyfutureSMS.action'])

        resp = self.session.post(_sent_verify_url, data=payload)

        soup = BeautifulSoup(resp.text, 'html.parser')

        msgs_lst = []
        msgs = soup.findAll('div', {'class': 'mess'})

        for msg in msgs:
            _mobile = str(msg.find('a').text)
            divrb = msg.find('div', {'class': 'rb'})
            _message = divrb.find('p').text
            original_message = '\n'.join(_message.splitlines()[1:-2])
            divbot = msg.find('div', {'class': 'bot'})
            _time = divbot.find('p', {'class': 'time'}).text

            msgs_lst.append([_mobile, original_message, _time])

        if [str(mobile), message, timestamp] in msgs_lst:
            return True
        else:
            return False

    def details(self, mobile):
        _main_url = '/'.join([self.base_url, 'LocateMobile/'+mobile])
        html = urllib.request.urlopen(_main_url)
        soup = BeautifulSoup(html.read(), 'html.parser')
        first = soup.find('div', {'id': 'info'})
        _mobile_detail = first.find_all('p')
        print()
        print(info(white('found details of Number: '+mobile)))
        for i in range(0,len(_mobile_detail)-1):
            print(good(lightgreen(_mobile_detail[i].get_text())))
        print()
