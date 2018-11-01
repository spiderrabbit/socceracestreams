import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmcaddon

import json, datetime, urllib2, time, base64, re




def fillcache():
  streams = {'retrieved':int(time.time()), 'data':[]}
  request = urllib2.Request('https://www.reddit.com/r/soccerstreams/search.json?sort=new&restrict_sr=on&q=GMT', headers={'User-agent': 'Kodi soccerstreams bot 0.1'})
  r = urllib2.urlopen(request).read()
  result = json.loads(r)
  #print result['data']['children']
  for p in result['data']['children']:
    if re.search(r'GMT',p['data']['title']):
      links=[]
      #print p['data']['title']
      #print p['data']['url']
      r = requests.get('%ssearch.json' % (p['data']['url']), headers = {'User-agent': 'Kodi soccerstreams bot 0.1'})
      comments = json.loads(r.text)
      for c in comments[1]['data']['children']:
        getreplies(c['data'])#recursively fetch replies
      streams['data'].append({'title':p['data']['title'], 'links':links})
  f =xbmcvfs.File ('special://temp/streamcache', 'w')
  f.write(json.dumps(streams))
  f.close()

def getfixtures(listing_type):
  today = datetime.datetime.today()
  rdata=[]
  headers = {'X-Auth-Token': '1ee91953768643e4acd30e197d9c033b'}
  if listing_type == 'main':
    url = 'http://api.football-data.org/v2/competitions?areas=2077&plan=TIER_ONE'
    request = urllib2.Request(url, headers=headers)
    r = urllib2.urlopen(request).read()
    data = json.loads(r)
    for l in data['competitions']:
      rdata.append({'name':'{0} ({1})'.format(l['name'], l['area']['name']), 'id':l['id']})
    return rdata
  else:
    url = 'http://api.football-data.org/v2/competitions/{0}/matches?dateFrom={1:%Y-%m-%d}&dateTo={2:%Y-%m-%d}'.format(listing_type, today, today + datetime.timedelta(days=7))
    request = urllib2.Request(url, headers=headers)
    r = urllib2.urlopen(request).read()
    data = json.loads(r)
    for l in data['matches']:
      rdata.append({ 'name':'{} vs {} {} {}'.format(l['homeTeam']['name'].encode('utf-8'), l['awayTeam']['name'].encode('utf-8'), l['utcDate'][:10], l['utcDate'][11:16]), 'status':l['status'] })
    return rdata


def build_url(query):
  return base_url + '?' + urllib.urlencode(query)

def mainmenu():
  li = xbmcgui.ListItem("View Leagues", iconImage='DefaultVideo.png')
  url = build_url({'mode': 'leagues'})
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  li = xbmcgui.ListItem("Live Streams", iconImage='DefaultVideo.png')
  url = build_url({'mode': 'livestreams'})
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  li = xbmcgui.ListItem("Scheduled recordings", iconImage='DefaultVideo.png')
  url = build_url({'mode': 'torecord'})
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
  
def getreplies(data):
  verified = False
  try:
    if data['author_flair_text'] is not None:
      if re.search('Verified', data['author_flair_text'], re.IGNORECASE): verified = True
  except:
    pass
  try:
    acestreams = re.findall(r'acestream://([0-9a-z]+)', data['body'])
    for a in acestreams:
      links.append({'acestream':a, 'verified':verified})
  except:
    pass
  try:
    if data['replies']!="":
      for reply in data['replies']['data']['children']:
        getreplies(reply['data'])
  except:
    pass


#xbmc.log("Playing: ".format()) 
        
addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, 'movies')
args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)
base_url = sys.argv[0]

settings = xbmcaddon.Addon('plugin.video.socceracestreams')
base64string = base64.encodestring('{0}:{1}'.format(settings.getSetting('username'), settings.getSetting('password')) ).replace('\n', '')

if mode is None:
  mainmenu()
  
elif mode[0]== 'livestreams':
  request = urllib2.Request('https://www.reddit.com/r/soccerstreams/search.json?sort=new&restrict_sr=on&q=GMT%20OR%20BST')
  request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
  result = urllib2.urlopen(request)
  data = json.loads(result.read())
  for c in data['data']['children']:
    if re.search("vs",c['data']['title']):
      url = build_url({'mode': 'livestream_detail', 'link': (c['data']['url']+'search.json').encode('utf-8')})
      li = xbmcgui.ListItem(c['data']['title'], iconImage='DefaultVideo.png')
      xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0]== 'livestream_detail':
  if not xbmc.Player().isPlaying():#not playing stop acestream server
    request = urllib2.Request("{0}://{1}/interface.php?action=stopstream".format(settings.getSetting('protocol'), settings.getSetting('domain')) )
    request.add_header("Authorization", "Basic %s" % base64string)
    result = urllib2.urlopen(request)
  
  url = 'https://{0}'.format(urllib.quote(args['link'][0][8:]))
  xbmc.log(url)
  request = urllib2.Request(url)
  request.add_header('User-agent', 'Kodi soccerstreams bot 0.1')
  result = urllib2.urlopen(request)
  data = json.loads(result.read())
  links = []
  for c in data[1]['data']['children']:
    getreplies(c['data'])#recursively fetch replies
  linkused = []
  for l in links:
    if l['acestream'] not in linkused:
      url = build_url({'mode': 'startlivestream', 'link': l['acestream']})
      if l['verified']: title = 'VERIFIED {}'.format(l['acestream'])
      else: title = l['acestream']
      li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png')
      linkused.append(l['acestream'])
      li.setProperty('IsPlayable' , 'true')
      xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
  xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0]== 'startlivestream':
  #send request to start stream
  request = urllib2.Request("{0}://{1}/interface.php?action=playstream&stream_id={2}".format(settings.getSetting('protocol'), settings.getSetting('domain'), args['link'][0]) )
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  progress = xbmcgui.DialogProgress()
  progress.create('Loading stream')
  for i in range (0,100,5):
    progress.update(i, "", '', "")
    time.sleep(1)
  # Create a playable item with a path to play.
  path = '{}://{}:{}@{}/segments/acestream.m3u8'.format(settings.getSetting('protocol'), settings.getSetting('username'), settings.getSetting('password'), settings.getSetting('domain'))
  play_item = xbmcgui.ListItem(path=path)
  # Pass the item to the Kodi player.
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

elif mode[0]== 'leagues':
  
  results = getfixtures('main') 
  
  #[{'name': u'Premier League (England)', 'id': 2021}, {'name': u'Championship (England)', 'id': 2016}, {'name': u'European Championship (Europe)', 'id': 2018}, {'name': u'UEFA Champions League (Europe)', 'id': 2001}, {'name': u'Ligue 1 (France)', 'id': 2015}, {'name': u'Bundesliga (Germany)', 'id': 2002}, {'name': u'Serie A (Italy)', 'id': 2019}, {'name': u'Eredivisie (Netherlands)', 'id': 2003}, {'name': u'Primeira Liga (Portugal)', 'id': 2017}, {'name': u'Primera Division (Spain)', 'id': 2014}]

  for f in results:
    url = build_url({'mode': 'leaguegame', 'foldername': 'league_%s' % f['id']})
    li = xbmcgui.ListItem(f['name'], iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'leaguegame':
  foldername = args['foldername'][0]
  lid = foldername[7:]
  results = getfixtures(lid)
  for f in results:
    url = build_url({'mode': 'game', 'foldername': f['name']})
    li = xbmcgui.ListItem(f['name'], iconImage='DefaultVideo.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
    
elif mode[0] == 'game':
  url = build_url({'mode': 'gamerecord', 'foldername': args['foldername'][0]})
  li = xbmcgui.ListItem("Record", iconImage='DefaultVideo.png')
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0] == 'gamerecord':
  #send request for game record
  request = urllib2.Request("{0}://{1}/interface.php?action=record&name={2}".format(settings.getSetting('protocol'), settings.getSetting('domain'), args['foldername'][0]) )
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  mainmenu()

elif mode[0] == 'torecord':
  request = urllib2.Request('{0}://{1}/interface.php?action=torecord'.format(settings.getSetting('protocol'), settings.getSetting('domain')))
  request.add_header("Authorization", "Basic {0}".format(base64string))
  result = urllib2.urlopen(request)
  data = json.loads(result.read())
  if data is not None:
    for m in data:
      url = build_url({'mode': 'torecorddetail', 'foldername': m.encode('utf-8')})
      li = xbmcgui.ListItem(m, iconImage='DefaultVideo.png')
      xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
    
  
