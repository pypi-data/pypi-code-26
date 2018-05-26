#!/usr/bin/env python
# coding: utf8

"""Doctring of the script"""


api_key = 'e38cc7822bd7476fe4083e36ee69748e'
username = 'werdeil'

import requests

from optparse import OptionParser

other = "/2.0/?method=track.getInfo&api_key=YOUR_API_KEY&artist=cher&track=believe&format=json"

url = "http://ws.audioscrobbler.com/2.0/?method=user.getartisttracks&user={0}&artist={1}&api_key={2}&format=json"
url2 = "http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key={0}&artist={1}&track={2}&username={3}&format=json"

from Foundation import *
from ScriptingBridge import *

import time

def update_playcount(iTunes):

    current =  iTunes.currentTrack()
    playcount = current.playedCount()

    response = requests.get(url2.format(api_key, current.artist().encode('utf-8'), current.name().encode('utf-8'), username))

    response_json = response.json()
    last_playcount = response_json["track"].get("userplaycount", 0)

    print last_playcount, playcount

    if playcount < int(last_playcount):
        print "updating playcount"
        current.setPlayedCount_(int(last_playcount))
    # current.setRating_(100)

    # for track in iTunes.tracks():
    #     print track.artist()
    #     print track.name()
    #     print track.albumArtist()
    #     print track.rating()
    #     print track.album()

def test_lastplay(iTunes):

    track = iTunes.tracks()[0]
    import pdb; pdb.set_trace()
    track.setPlayedDate_(datetime.datetime(2017,12,30,18,13,14,0000))
    datetime.datetime.fromtimestamp(1515697518)

def test50cent(iTunes):
    tracks = iTunes.tracks()
    print len(tracks)
    i = 1
    for track in tracks:
        print track.artist(), track.name(), i
        i += 1
            

if __name__ == "__main__":
    iTunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")
    
    test50cent(iTunes)
