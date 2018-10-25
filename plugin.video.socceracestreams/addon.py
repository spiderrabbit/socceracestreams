import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcvfs
import xbmcaddon

import json, datetime, urllib2, time, base64


settings = xbmcaddon.Addon('plugin.video.socceracestreams')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

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
  headers = {'X-Auth-Token': "1ee91953768643e4acd30e197d9c033b"}
  if listing_type == "main":
    url = "http://api.football-data.org/v2/competitions?areas=2077&plan=TIER_ONE"
    request = urllib2.Request(url, headers=headers)
    r = urllib2.urlopen(request).read()
    data = json.loads(r)
    for l in data['competitions']:
      rdata.append({'name':"%s (%s)" % (l['name'], l['area']['name']), 'id':l['id']})
    return rdata
  else:
    url = "http://api.football-data.org/v2/competitions/%s/matches?dateFrom=%s&dateTo=%s" % (listing_type, today.strftime("%Y-%m-%d"), (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"))
    request = urllib2.Request(url, headers=headers)
    r = urllib2.urlopen(request).read()
    data = json.loads(r)
    for l in data['matches']:
      #print  l['utcDate']
      
      rdata.append({'name':"%s vs %s %s %s" % (l['homeTeam']['name'], l['awayTeam']['name'], l['utcDate'][:10], l['utcDate'][11:16]), 'status':l['status']})
    return rdata
  
#if xbmcvfs.exists('special://temp/streamcache'):
  #f = xbmcvfs.File ('special://temp/streamcache', 'r')
  #streams = json.loads(f.read())
  #f.close()
  #if time.time() - streams['retrieved'] > 300:#refresh cache every 5 mins
    #fillcache()
    #f = xbmcvfs.File ('special://temp/streamcache', 'r')
    #streams = json.loads(f.read())
    #f.close()
#else:
  #fillcache()

xbmcplugin.setContent(addon_handle, 'movies')

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def mainmenu():
  results = getfixtures('main') 
  
  #[{'name': u'Premier League (England)', 'id': 2021}, {'name': u'Championship (England)', 'id': 2016}, {'name': u'European Championship (Europe)', 'id': 2018}, {'name': u'UEFA Champions League (Europe)', 'id': 2001}, {'name': u'Ligue 1 (France)', 'id': 2015}, {'name': u'Bundesliga (Germany)', 'id': 2002}, {'name': u'Serie A (Italy)', 'id': 2019}, {'name': u'Eredivisie (Netherlands)', 'id': 2003}, {'name': u'Primeira Liga (Portugal)', 'id': 2017}, {'name': u'Primera Division (Spain)', 'id': 2014}]

  for f in results:
    url = build_url({'mode': 'folder', 'foldername': 'league_%s' % f['id']})
    li = xbmcgui.ListItem(f['name'], iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)
  
  li = xbmcgui.ListItem("TO RECORD", iconImage='DefaultVideo.png')
  url = 'https://localhost/listings/live_stream_from_start.mp4'
  xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)
  xbmcplugin.endOfDirectory(addon_handle)
  
mode = args.get('mode', None)

if mode is None:
  mainmenu()

elif mode[0] == 'folder':
  foldername = args['foldername'][0]
  lid = foldername[7:]
  results = getfixtures(lid)
  for f in results:
    url = build_url({'mode': 'game', 'foldername': f['name'].encode('utf-8')})
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
  request = urllib2.Request("https://%s/interface.php?action=record&name=%s" % (settings.getSetting('domain'), args['foldername'][0]) )
  base64string = base64.encodestring('%s:%s' % (settings.getSetting('username'), settings.getSetting('password')) ).replace('\n', '')
  request.add_header("Authorization", "Basic %s" % base64string)
  result = urllib2.urlopen(request)
  mainmenu()
