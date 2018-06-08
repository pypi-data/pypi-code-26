from __future__ import unicode_literals
import youtube_dl
import hashlib
import hmac
import time
import requests
import os
import json

def fileSafe(filename):
    replaceCharacter = '-'
    unsafeCharacters = ['\\', '/',':','*','?','"', '<', '>', '|', '\n']
    safe = []
    for l in filename:
        if l in unsafeCharacters:
            safe.append(replaceCharacter)
        else:
            safe.append(l)
    safe = ''.join(safe)
    return safe

def download(showLink, show, tvid, downloadPath):
    if not os.path.exists('Logs'):
        os.makedirs('Logs')
    urls = []
    r = requests.get(showLink).json()
    houseNumber = r['episodeHouseNumber']
    urls.append(r['href'])
    if tvid != None:
        url = 'http://api.tvmaze.com/shows/{}/episodes'.format(tvid)
        tvMazeR = requests.get(url).json()
    url = 'https://iview.abc.net.au/api/related/{}'.format(houseNumber)
    data = requests.get(url).json()
    try:
        for link in data['index'][0]['episodes']:
            urls.append(link['href'])
    except NameError:
        pass
    try:
        downloaded = open('Logs/{}.json'.format(show), 'r')
        downloaded = json.loads(downloaded.read())
        newShow = False
    except FileNotFoundError:
        downloaded = []
        newShow = True
    for url in urls:
        url = 'https://iview.abc.net.au/api/{}'.format(url)
        data = requests.get(url).json()
        house_number = data['episodeHouseNumber']
        if house_number in [d['houseNumber'] for d in downloaded]:
            pass
        else:
            path = '/auth/hls/sign?ts={0}&hn={1}&d=android-mobile'.format(
                int(time.time()), house_number)
            sig = hmac.new(
                'android.content.res.Resources'.encode('utf-8'),
                path.encode('utf-8'), hashlib.sha256).hexdigest()
            token ='http://iview.abc.net.au{0}&sig={1}'.format(path, sig)
            token = requests.get(token).text
            stream = '{}?hdnea={}'.format(data['playlist'][-1]['hls-plus'],token)
            if tvid==None:
                ep = fileSafe('{} - {}'.format(data['seriesTitle'], data['title']))
            else:
                for n in tvMazeR:
                    if data['pubDate'].split(' ')[0]==n['airdate']:
                        if len(str(n['number']))==1:
                            epnum=str('0'+str(n['number']))
                        else:
                            epnum=str(n['number'])
                        if len(str(n['season']))==1:
                            season=str('0'+str(n['season']))
                        else:
                            season=str(n['season'])
                        ep = fileSafe('{} - S{}E{} - {}'.format(show, season, epnum, n['name']))
            if downloadPath != None:
                if downloadPath[-1] == '/' or downloadPath[-1] == '\\':
                    pass
                else:
                    downloadPath = downloadPath + '/'
                downloadPath = downloadPath.replace('\\', '/')
            else:
                downloadPath = os.getcwd().replace('\\', '/') + '/'
            if newShow == False:
                ydl_opts = {
                    'outtmpl': "{}{}.%(ext)s".format(downloadPath, ep)
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([stream])
            downloaded.append({'houseNumber': house_number, 'name': ep})
    with open('Logs/{}.json'.format(show), 'w') as file:
        downloaded = json.dumps(downloaded)
        file.write(downloaded)

