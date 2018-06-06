import http.client
import urllib
import argparse
import json

def argParse():
    parser = argparse.ArgumentParser()

    parser.add_argument('-u', metavar='<string>', help='pushover user token')
    parser.add_argument('-t', metavar='<string>', help='pushover app token')

    return parser.parse_args()


class Pushover:
    def __init__(self, user=None, token=None, target=None, url=None, url_title=None):
        self.url = url
        self.user = user
        self.token = token
        self.target = target
        self.url_title = url_title

    def sendMessage(self, message):
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
            urllib.parse.urlencode({
                "token": self.token,
                "user": self.user,
                "url": self.url,
                "url_title": self.url_title,
                "device": self.target,
                "message": message,
            }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
        if __name__ == '__main__':
            return conn.getresponse()

def main():
    args = argParse()

    userKeySet = args.user_key or args.user_key == ""
    appTokenSet = args.token or args.token == ""

    print(userKeySet)
    print(appTokenSet)

    if not userKeySet or not appTokenSet:
        # Handle this better... If not set, ask user.
        print("Set user key and token with -u and -t respectively.")
        print("Exiting...")
        exit()
    else:
        user = args.user_key
        token = args.token


    p = Pushover(user, token)
    p.sendMessage("Testing pushover.py")


if __name__ == '__main__':
    main()