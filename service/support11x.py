"""
---------------------
LocatorDelaySystem
Support Service V1.1X
---------------------
LOG
- added checking in
"""
import json,getpass,urllib2,urllib,os,sys
import datetime as dt
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

#--------------
# user
#--------------

#Check Info

#Time
date = dt.datetime.today()
value1 = urllib.quote_plus(str(date))

#User Info
data_set = {}
try:
    with open(userFile, 'r') as f:
        data_set = json.load(f)
except:
    data_set['email'] = 'user not found  '+ script_dirpath
    pass
user = str(getpass.getuser()).upper()
ma_ver = 'MAYA'+str(cmds.about(version=True))
ip_host = str(urllib2.urlopen('https://v4.ident.me', timeout=5).read().decode('utf8'))
value2_list = [data_set['email'],user,ma_ver,ip_host]
value2 = ','.join(value2_list)
value2 = urllib.quote_plus(value2)

#Action
value3_list = [str(data_set['version'])]
value3 = ','.join(value3_list)
value3 = urllib.quote_plus(value3)
url = 'https://maker.ifttt.com/trigger/brs_locDlay/with/key/lt6C8G5VRbvc2fOnGjmS5_4J9A_fwtNjQ2VQJ6fO5YK?value1='+value1+'&value2='+value2+'&value3='+value3
urllib2.urlopen(url, timeout=5).read()


# Supporter Coding
# Force Update for 1 month since 1 oct 2020
try:
    updateSource = 'source "'+projectDir.replace('\\','/') + '/BRS_DragNDrop_Update.mel' + '";'
    mel.eval(updateSource)
except:
    pass
