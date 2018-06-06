# -*- coding: utf-8 -*-
try:
    import requests
    import click
    import codecs
    import zipfile
    import io
    import os
    import re
    from scrapy.selector import Selector
    from pprint import pprint
except:
    pass

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fix_encoding(text):
  grade = lambda s: len([s.count(c) for c in u'ąćńłżźę' if s.count(c) > 5])
  try:
    decoded = []
    for e in ['windows-1250', 'iso-8859-2', 'utf-8', 'utf-16', 'utf-32']:
      try:
        decoded.append(text.decode(e, 'ignore'))
      except:
        pass
    text = sorted(decoded, key=grade, reverse=True)[0].encode('utf-8')
  except:
    pass
  text = text[3:] if text[0:3] == codecs.BOM_UTF8 else text
  return text

p = {
  'headers': {
    "Accept-Language": "en,pl;q=0.8", 
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36",
  },
  'verify': False
}

BASE = 'https://www.podnapisi.net'

def getsubs(url, target_fn, fix_enc=False):
  click.echo('Downloading ', nl=False)
  click.secho(url, fg='yellow')
  
  r = requests.get(url, **p)
  z = zipfile.ZipFile(io.BytesIO(r.content))
  zf = z.filelist[0]
  fn = target_fn + os.path.splitext(zf.filename)[1]
  with open(fn, 'wb') as f:
    subs = z.read(zf)
    f.write(fix_encoding(subs) if fix_enc else subs)
  click.echo('Saved ', nl=False)
  click.secho(fn, fg='yellow')
  return fn

def find_movie(title, target_fn):
  r = requests.get(BASE + '/subtitles/search/', params={'keywords': title}, **p)
  # print r.url
  s = Selector(text=r.text)
  movies = s.css('.movie_item')
  if len(movies) > 0:
    for i, movie in enumerate(movies, 1):
      name = movie.css('.title').xpath('*/span/text()').extract_first()
      click.echo("%i. %s" % (i, name))
      
    sel = click.prompt('Your choice', default=0)
    if sel == 0: return
    r = requests.get(BASE + movies[sel-1].xpath('@href').extract_first(), params={'keywords': title}, **p)
    select_subtitle(r.text, target_fn)
  else:
    select_subtitle(r.text, target_fn)

def select_subtitle(html, target_fn):
  s = Selector(text=html)

  entries = [{
    'n': i,
    'link': BASE + (e.css('a').xpath('@href').extract_first() or ''),
    'release': e.css('.release').xpath('text()').extract_first(),
    'lang': e.css('.language').xpath('*/text()').extract_first(),
    'fps': e.xpath('td[3]/text()').extract_first(),
    'downloads': e.xpath('td[7]/text()').extract_first()
  } for i, e in enumerate(s.css('.subtitle-entry'), 1)]


  if not len(entries):
    click.echo('Nothing found')
    return
  
  click.echo('Releases:')
  for e in entries:
    click.echo('%(n)2d. %(lang)3s %(fps)5s %(downloads)4s %(release)s' % e)
  
  click.echo()
  last_fn = None
  while True:
    sel = click.prompt('Your choice', default=0)
    if sel == 0: break

    e = entries[abs(sel)-1]
    if sel > 0 and last_fn and os.path.isfile(last_fn):
      click.secho('Removing %s...' % last_fn, fg='red')
      os.remove(last_fn)
    last_fn = getsubs(e['link'], target_fn, e['lang'] and e['lang'].strip() == 'pl')

@click.command(help="Download movie subtitles from podnapisi website")
@click.argument('filename')
def pn(filename):
  if os.path.isfile(filename):
    basename, ext = os.path.splitext(filename)
    search = re.findall('.+s\d{2}e\d{2}', basename, re.I)
    search = search[0] if search else basename
    search = search.replace('.', ' ')
  else:
    basename = filename
    search = filename
  click.echo('Searching %s...' % search)
  find_movie(search, basename)
