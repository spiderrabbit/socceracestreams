import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmcaddon

import json, datetime, urllib2, time, base64, re

#def fillcache():
  #streams = {'retrieved':int(time.time()), 'data':[]}
  #request = urllib2.Request('https://www.reddit.com/r/soccerstreams/search.json?sort=new&restrict_sr=on&q=GMT', headers={'User-agent': 'Kodi soccerstreams bot 0.1'})
  #r = urllib2.urlopen(request).read()
  #result = json.loads(r)
  ##print result['data']['children']
  #for p in result['data']['children']:
    #if re.search(r'GMT',p['data']['title']):
      #links=[]
      ##print p['data']['title']
      ##print p['data']['url']
      #r = requests.get('%ssearch.json' % (p['data']['url']), headers = {'User-agent': 'Kodi soccerstreams bot 0.1'})
      #comments = json.loads(r.text)
      #for c in comments[1]['data']['children']:
        #getreplies(c['data'])#recursively fetch replies
      #streams['data'].append({'title':p['data']['title'], 'links':links})
  #f =xbmcvfs.File ('special://temp/streamcache', 'w')
  #f.write(json.dumps(streams))
  #f.close()

#def getfixtures(listing_type):
  #today = datetime.datetime.today()
  #rdata=[]
  #headers = {'X-Auth-Token': '1ee91953768643e4acd30e197d9c033b'}
  #if listing_type == 'main':
    #url = 'http://api.football-data.org/v2/competitions?areas=2077&plan=TIER_ONE'
    #request = urllib2.Request(url, headers=headers)
    #r = urllib2.urlopen(request).read()
    #data = json.loads(r)
    #for l in data['competitions']:
      #rdata.append({'name':'{0} ({1})'.format(l['name'], l['area']['name']), 'id':l['id']})
    #return rdata
  #else:
    #url = 'http://api.football-data.org/v2/competitions/{0}/matches?dateFrom={1:%Y-%m-%d}&dateTo={2:%Y-%m-%d}'.format(listing_type, today, today + datetime.timedelta(days=7))
    #request = urllib2.Request(url, headers=headers)
    #r = urllib2.urlopen(request).read()
    #data = json.loads(r)
    #for l in data['matches']:
      #rdata.append({ 'name':'{} vs {} {} {}'.format(l['homeTeam']['name'].encode('utf-8'), l['awayTeam']['name'].encode('utf-8'), l['utcDate'][:10], l['utcDate'][11:16]), 'status':l['status'] })
    #return rdata


def build_url(query):
  return base_url + '?' + urllib.urlencode(query)

def mainmenu():
  li = xbmcgui.ListItem("View Leagues", iconImage='DefaultVideo.png')
  url = build_url({'mode': 'leagues'})
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  li = xbmcgui.ListItem("Live Streams", iconImage='DefaultVideo.png')
  url = build_url({'mode': 'livestreams'})
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  li = xbmcgui.ListItem("Recordings", iconImage='DefaultVideo.png')
  url = build_url({'mode': 'torecord'})
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  request = urllib2.Request("{0}://{1}/interface.php?action=status".format(settings.getSetting('protocol'), settings.getSetting('domain')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  results  = json.loads(result.read())
  if 'current_recording' in results:
    li = xbmcgui.ListItem("Currently recording", iconImage='DefaultVideo.png')
    url = build_url({'mode': 'currentlyrecording'})
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
livestreampath = '{}://{}:{}@{}/listings/LIVE.m3u8'.format(settings.getSetting('protocol'), settings.getSetting('username'), settings.getSetting('password'), settings.getSetting('domain'))

if mode is None:
  mainmenu()
  
elif mode[0]== 'currentlyrecording':
  request = urllib2.Request("{0}://{1}/interface.php?action=status".format(settings.getSetting('protocol'), settings.getSetting('domain')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  results  = json.loads(result.read())
  if 'current_recording' in results:
    li = xbmcgui.ListItem(results['current_recording'], iconImage='DefaultVideo.png')
    url = livestreampath
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
    url = build_url({'mode': 'stoprecording'})
    li = xbmcgui.ListItem('Stop recording', iconImage='DefaultVideo.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)

elif mode[0]== 'stoprecording':
  request = urllib2.Request("{0}://{1}/interface.php?action=stopstream".format(settings.getSetting('protocol'), settings.getSetting('domain')) )
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)  
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
  play_item = xbmcgui.ListItem(path=livestreampath)
  # Pass the item to the Kodi player.
  xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

elif mode[0]== 'leagues':
  #results = getfixtures('main') 
  request = urllib2.Request("{0}://{1}/footballscraper.php?date={2}".format(settings.getSetting('protocol'), settings.getSetting('domain'), datetime.datetime.today().strftime('%Y-%m-%d')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  results  = json.loads(result.read())
  #[{'name': u'Premier League (England)', 'id': 2021}, {'name': u'Championship (England)', 'id': 2016}, {'name': u'European Championship (Europe)', 'id': 2018}, {'name': u'UEFA Champions League (Europe)', 'id': 2001}, {'name': u'Ligue 1 (France)', 'id': 2015}, {'name': u'Bundesliga (Germany)', 'id': 2002}, {'name': u'Serie A (Italy)', 'id': 2019}, {'name': u'Eredivisie (Netherlands)', 'id': 2003}, {'name': u'Primeira Liga (Portugal)', 'id': 2017}, {'name': u'Primera Division (Spain)', 'id': 2014}]

  for f in sorted(results):
    url = build_url({'mode': 'leaguedate', 'leaguename': f})
    li = xbmcgui.ListItem(f, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'leaguedate':
  request = urllib2.Request("{0}://{1}/footballscraper.php?date={2}".format(settings.getSetting('protocol'), settings.getSetting('domain'), datetime.datetime.today().strftime('%Y-%m-%d')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  results  = json.loads(result.read())
  for f in sorted(results[args['leaguename'][0]]):
    url = build_url({'mode': 'leaguegame', 'leaguename': args['leaguename'][0], 'leaguedate': f})
    li = xbmcgui.ListItem(f, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'leaguegame':
  request = urllib2.Request("{0}://{1}/footballscraper.php?date={2}".format(settings.getSetting('protocol'), settings.getSetting('domain'), datetime.datetime.today().strftime('%Y-%m-%d')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  results  = json.loads(result.read())
  for f in results[args['leaguename'][0]][args['leaguedate'][0]]:
    url = build_url({'mode': 'game', 'match': f.encode('utf-8')})
    li = xbmcgui.ListItem(f, iconImage='DefaultVideo.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
    
elif mode[0] == 'game':
  url = build_url({'mode': 'gamerecord', 'match': args['match'][0]})
  li = xbmcgui.ListItem("Record", iconImage='DefaultVideo.png')
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0] == 'gamerecord':
  #send request for game record
  request = urllib2.Request("{0}://{1}/interface.php?{2}".format(settings.getSetting('protocol'), settings.getSetting('domain'), urllib.urlencode({'name':args['match'][0], 'action':'record'})) )
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  mainmenu()

elif mode[0] == 'torecord':
  request = urllib2.Request('{0}://{1}/interface.php?action=listings'.format(settings.getSetting('protocol'), settings.getSetting('domain')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  #'{"F33GH3XO": "Manchester United vs Huddersfield Town 2018-12-26 15:00_1","53SQFEB4": "Manchester United vs Huddersfield Town 2018-12-26 15:00_2","LACH0304": "TRANSCODED_Manchester United vs Huddersfield Town 2018-12-26 15:00_1"}\n'
  data = json.loads(result.read())
  if data is not None:
    out=[]
    for m in data:
      if data[m][:10]!="TRANSCODED":#don't include value with TRANSCOSE - auto find these later when pressing play, second choice is non transcoded
        out.append('{}|{}'.format(data[m],m))
    out.sort()

    for m in out:#print sorted list
      v = m.split('|')
      url = build_url({'mode': 'playmatch', 'recording_name': v[1]})
      li = xbmcgui.ListItem(v[0], iconImage='DefaultVideo.png')
      xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0] == 'playmatch':
  request = urllib2.Request('{0}://{1}/interface.php?action=listings'.format(settings.getSetting('protocol'), settings.getSetting('domain')))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  data = json.loads(result.read())
  if data is not None:
    for m in data:
      if m == args['recording_name'][0]:#found match
        toplayname = data[m]
        toplaykey = m
    for m in data:#look for transcoded file prefix first
      if data[m] == 'TRANSCODED_{}'.format(toplayname):
        toplaykey = m
      
    # Create a playable item with a path to play.
    path = '{}://{}:{}@{}/store/{}.mp4'.format(settings.getSetting('protocol'), settings.getSetting('username'), settings.getSetting('password'), settings.getSetting('domain'), toplaykey)
    li = xbmcgui.ListItem('Play', iconImage='DefaultVideo.png')
    li.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=path, listitem=li, isFolder=False)
  xbmcplugin.endOfDirectory(addon_handle)  
      
  #request = urllib2.Request('{0}://{1}/interface.php?action=torecord'.format(settings.getSetting('protocol'), settings.getSetting('domain')))
  #request.add_header("Authorization", "Basic %s" % base64string)
  #result = urllib2.urlopen(request)
  #data = json.loads(result.read())
  #if data is not None:
    #for m in data:
      #url = build_url({'mode': 'torecorddetail', 'recording_name': m.encode('utf-8')})
      #li = xbmcgui.ListItem(m, iconImage='DefaultVideo.png')
      #xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  #xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0] == 'torecorddetail':
  url = build_url({'mode': 'deleterecording', 'recording_name': args['recording_name'][0]})
  li = xbmcgui.ListItem('Delete', iconImage='DefaultVideo.png')
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  xbmcplugin.endOfDirectory(addon_handle)
  
elif mode[0] == 'deleterecording':
  request = urllib2.Request('{0}://{1}/interface.php?{2}'.format(settings.getSetting('protocol'), settings.getSetting('domain'), urllib.urlencode({'name':args['recording_name'][0], 'action':'deleterecording'})))
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  mainmenu()
