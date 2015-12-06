# -*- coding: utf-8 -*-
# Esquire TV XBMC Addon

import sys,httplib
import urllib, urllib2, cookielib, datetime, time, re, os, string
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs, xbmc
import zlib,json,HTMLParser
h = HTMLParser.HTMLParser()
qp  = urllib.quote_plus
uqp = urllib.unquote_plus

UTF8     = 'utf-8'
ESQUIREBASE = 'http://tv.esquire.com%s'

addon         = xbmcaddon.Addon('plugin.video.esquire')
__addonname__ = addon.getAddonInfo('name')
__language__  = addon.getLocalizedString

home          = addon.getAddonInfo('path').decode(UTF8)
icon          = xbmc.translatePath(os.path.join(home, 'icon.png'))
addonfanart   = xbmc.translatePath(os.path.join(home, 'fanart.jpg'))


def log(txt):
    message = '%s: %s' % (__addonname__, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)

USER_AGENT = 'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25'
defaultHeaders = {'User-Agent':USER_AGENT, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8'} 

def getRequest(url, headers = defaultHeaders):
   log("getRequest URL:"+str(url))
   req = urllib2.Request(url.encode(UTF8), None, headers)
   try:
      response = urllib2.urlopen(req)
      page = response.read()
      if response.info().getheader('Content-Encoding') == 'gzip':
         log("Content Encoding == gzip")
         page = zlib.decompress(page, zlib.MAX_WBITS + 16)
   except:
      page = ""
   return(page)

def getShows():
   xbmcplugin.setContent(int(sys.argv[1]), 'files')
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_UNSORTED)
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_TITLE)
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_EPISODE)

   ilist=[]
   html = getRequest('http://tv.esquire.com/now/')
   blob = re.compile('<div class="shows">(.+?)</div',re.DOTALL).search(html).group(1)
   cats = re.compile('<a href="(.+?)".+?>(.+?)</a',re.DOTALL).findall(blob)
   for url, name in cats:
       name = name.strip()
       name = h.unescape(name.decode(UTF8))
       url = ESQUIREBASE % (url)
       print "url = "+str(url)
       html = getRequest(url)
       try:    fanart = re.compile('<img class="showBaner" src="(.+?)"',re.DOTALL).search(html).group(1)
       except: fanart = addonfanart
       try:    plot = re.compile('"twitter:description" content="(.+?)"',re.DOTALL).search(html).group(1)
       except: plot = ''
       html = re.compile("Drupal\.settings, (.+?)\);<",re.DOTALL).search(html).group(1)
       a = json.loads(html)
       try:    b = a["tve_widgets"]["clone_of_latest_episodes"]["assets1"][0]
       except: continue
       infoList = {}
       dstr = (b['aired_date'].split('-'))
       infoList['Date']        = '%s-%s-%s' % (dstr[2], dstr[0].zfill(2), dstr[1].zfill(2))
       infoList['Aired']       = infoList['Date']
       infoList['MPAA']        = ''
       infoList['TVShowTitle'] = b['show_title']
       infoList['Title']       = b['show_title']
       infoList['Studio']      = 'Esquire TV'
       infoList['Genre']       = ''
       infoList['Episode']     = int(a["tve_widgets"]["clone_of_latest_episodes"]["assets_number"])
       infoList['Year']        = int(infoList['Aired'].split('-',1)[0])
       infoList['Plot']        = h.unescape(plot.decode(UTF8))
       mode = 'GE'
       u = '%s?url=%s&name=%s&mode=%s' % (sys.argv[0],qp(url), qp(name), mode)
       liz=xbmcgui.ListItem(name, '',icon, None)
       liz.setInfo( 'Video', infoList)
       liz.setProperty('fanart_image', fanart)
       ilist.append((u, liz, True))
   xbmcplugin.addDirectoryItems(int(sys.argv[1]), ilist, len(ilist))
   if addon.getSetting('enable_views') == 'true':
      xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.getSetting('default_view'))
   xbmcplugin.endOfDirectory(int(sys.argv[1]))


def getEpisodes(eurl, showName):
   xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_UNSORTED)
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_TITLE)
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_VIDEO_YEAR)
   xbmcplugin.addSortMethod(int(sys.argv[1]),xbmcplugin.SORT_METHOD_EPISODE)

   ilist=[]        
   html = getRequest(eurl)
   try:    fanart = re.compile('<img class="showBaner" src="(.+?)"',re.DOTALL).search(html).group(1)
   except: fanart = addonfanart
   html = re.compile("Drupal\.settings, (.+?)\);<",re.DOTALL).search(html).group(1)
   a = json.loads(html)
   mode = 'GV'
   for b in a["tve_widgets"]["clone_of_latest_episodes"]["assets1"]:
      infoList = {}
      dstr = (b['aired_date'].rsplit('-'))
      infoList['Date']        = '%s-%s-%s' % (dstr[2], dstr[0].zfill(2), dstr[1].zfill(2))
      infoList['Aired']       = infoList['Date']
      infoList['MPAA']        = ''
      infoList['TVShowTitle'] = b['show_title']
      infoList['Title']       = b['episode_title']
      infoList['Studio']      = 'Esquire TV'
      infoList['Genre']       = ''
      infoList['Season']      = b['season_n']
      infoList['Episode']     = b['episode_n']
      infoList['Year']        = int(infoList['Aired'].split('-',1)[0])
      infoList['Plot']        = h.unescape(b["synopsis"])
      thumb = b["episode_thumbnail"]["url"]
      url   = b['link']
      name  = b['episode_title']
      u = '%s?url=%s&name=%s&mode=%s' % (sys.argv[0],qp(url), qp(name), mode)
      liz=xbmcgui.ListItem(name, '',None, thumb)
      liz.setInfo( 'Video', infoList)
      liz.addStreamInfo('video', { 'codec': 'h264', 
                                   'width' : 1920, 
                                   'height' : 1080, 
                                   'aspect' : 1.78 })
      liz.addStreamInfo('audio', { 'codec': 'aac', 'language' : 'en'})
      liz.addStreamInfo('subtitle', { 'language' : 'en'})
      liz.setProperty('fanart_image', fanart)
      liz.setProperty('IsPlayable', 'true')
      ilist.append((u, liz, False))
   xbmcplugin.addDirectoryItems(int(sys.argv[1]), ilist, len(ilist))
   if addon.getSetting('enable_views') == 'true':
      xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.getSetting('episode_view'))
   xbmcplugin.endOfDirectory(int(sys.argv[1]))


def getVideo(url, show_name):
    gvu1 = 'https://tveesquire-vh.akamaihd.net/i/prod/video/%s_,1696,1296,896,696,496,240,306,.mp4.csmil/master.m3u8?__b__=1000&hdnea=st=%s~exp=%s'
    url = ESQUIREBASE % uqp(url)
    html = getRequest(url)
    url = re.compile('data-release-url="(.+?)"',re.DOTALL).search(html).group(1)
    url = 'http:'+url+'&player=Esquire%20VOD%20Player%20%28Phase%203%29&format=Script&height=576&width=1024'
    html = getRequest(url)

    a = json.loads(html)
    suburl = a["captions"][0]["src"]
    url = suburl.split('/caption/',1)[1]
    url = url.split('.',1)[0]
    td = (datetime.datetime.utcnow()- datetime.datetime(1970,1,1))
    unow = int((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6)
    u   =  gvu1 % (url, str(unow), str(unow+60))
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path = u))

    if (addon.getSetting('sub_enable') == "true"):
      profile = addon.getAddonInfo('profile').decode(UTF8)
      subfile = xbmc.translatePath(os.path.join(profile, 'SyfySubtitles.srt'))
      prodir  = xbmc.translatePath(os.path.join(profile))
      if not os.path.isdir(prodir):
         os.makedirs(prodir)

      pg = getRequest(suburl)
      if pg != "":
        ofile = open(subfile, 'w+')
        captions = re.compile('<p begin="(.+?)" end="(.+?)">(.+?)</p>',re.DOTALL).findall(pg)
        idx = 1
        for cstart, cend, caption in captions:
          cstart = cstart.replace('.',',')
          cend   = cend.replace('.',',').split('"',1)[0]
          caption = caption.replace('<br/>','\n').replace('&gt;','>').replace('&apos;',"'").replace('&quot;','"')
          ofile.write( '%s\n%s --> %s\n%s\n\n' % (idx, cstart, cend, caption))
          idx += 1
        ofile.close()
        xbmc.sleep(2000)
        xbmc.Player().setSubtitles(subfile)

# MAIN EVENT PROCESSING STARTS HERE

parms = {}
try:
    parms = dict( arg.split( "=" ) for arg in ((sys.argv[2][1:]).split( "&" )) )
    for key in parms:
      try:    parms[key] = urllib.unquote_plus(parms[key]).decode(UTF8)
      except: pass
except:
    parms = {}

p = parms.get

mode = p('mode',None)

if mode==  None:  getShows()
elif mode=='GE':  getEpisodes(p('url'), p('name'))
elif mode=='GV':  getVideo(p('url'), p('name'))