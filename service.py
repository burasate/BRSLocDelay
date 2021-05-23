"""
---------------------
LocatorDelaySystem
Support Service V1.1X
---------------------
"""

import json, getpass, os, time,urllib,os,sys
from time import gmtime, strftime
from datetime import datetime as dt
from maya import mel
import maya.cmds as cmds

def formatPath(path):
    import os
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path

mayaAppDir = formatPath(mel.eval('getenv MAYA_APP_DIR'))
scriptsDir = formatPath(mayaAppDir + os.sep + 'scripts')
projectDir = formatPath(scriptsDir + os.sep + 'BRSLocDelay')
presetsDir = formatPath(projectDir + os.sep + 'presets')
userFile = formatPath(projectDir + os.sep + 'user')
configFile = formatPath(projectDir + os.sep + 'config.json')

def BRSEventStop(eventName='',eventStartTime=0.0,selectList=[],mode='',distance=0.0,dynamic=0,offset=0.0,isSmoothness=0,breakdown=0):
    if not eventName in ['open','ovelape','bake']:
        return None

    filepath = cmds.file(q=True, sn=True)
    filename = os.path.basename(filepath)
    raw_name, extension = os.path.splitext(filename)
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    eventStopTime = time.time()

    userData = json.load(open(userFile, 'r'))
    data = {
        'dateTime' : dt.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timezone' : str( strftime('%z', gmtime()) ),
        'year' : dt.now().strftime('%Y'),
        'month' : dt.now().strftime('%m'),
        'day' : dt.now().strftime('%d'),
        'hour' : dt.now().strftime('%H'),
        'email' : userData['email'],
        'user' : getpass.getuser(),
        'maya' : str(cmds.about(version=True)),
        'ip' : str(urllib2.urlopen('https://v4.ident.me', timeout=5).read().decode('utf8')),
        'version' : userData['version'],
        'scene' : raw_name,
        'timeUnit' : cmds.currentUnit(q=True, t=True),
        'eventName' : eventName,
        'eventTime' : eventStopTime - eventStartTime,
        'timeMin' : minTime,
        'timeMax' : maxTime,
        'duration' : maxTime - minTime,
        'selectCount' : len(selectList),
        'selectList' : ','.join(selectList),
        'mode' : mode,
        'distance' : distance,
        'dynamic' : dynamic,
        'offset' : offset,
        'isSmoothness' : isSmoothness,
        'breakdown' : breakdown,
        'lastUpdate' : userData['lastUsedDate'],
        'used' : userData['used'],
        'isTrial' : userData['isTrial'],
        'days' : userData['days'],
        'registerDate' : userData['registerDate'],
        'lastUsedDate' : userData['lastUpdate']
    }

    url = 'https://hook.integromat.com/gnjcww5lcvgjhn9lpke8v255q6seov35'
    params = urllib.urlencode(data)
    conn = urllib.urlopen('{}?{}'.format(url, params))
    print(conn.read())
    print(conn.info())
