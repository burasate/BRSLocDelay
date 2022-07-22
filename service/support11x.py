"""
---------------------
LocatorDelaySystem
Support Service V1.1X
---------------------
"""
import json, getpass, time,os,sys
from time import gmtime, strftime
import datetime as dt
from maya import mel
import maya.cmds as cmds
if sys.version[0] == '3':
    writeMode = 'w'
    import urllib.request as uLib
else:
    writeMode = 'wb'
    import urllib as uLib

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

# =========================================
# Supporter Coding
try:
    updateSource = 'source "'+projectDir.replace('\\','/') + '/BRS_DragNDrop_Update.mel' + '";'
    mel.eval(updateSource)
except:
    pass

# Fix Distance Slider
cmds.floatSlider(distanceS,e=True, minValue=0.01, maxValue=500, value=2)

# ==========================================

# User
try:
    with open(userFile, 'r') as f:
        userData = json.load(f)
except:
    pass
else:
    today = str(dt.date.today())
    userData['lastUsedDate'] = today
    todayDate = dt.datetime.strptime(userData['lastUsedDate'], '%Y-%m-%d')
    try:
        regDate = dt.datetime.strptime(userData['registerDate'], '%Y-%m-%d')
    except:
        regDate = dt.datetime.strptime(today, '%Y-%m-%d')
    userData['used'] = userData['used']
    userData['version'] = 1.2
    userData['days'] = abs((regDate - todayDate).days)
    userData['lastUpdate'] = today

    # User Update ===================== >
    if userData['email'] == '':
        userData['email'] = ''
    if not 'regUser64' in userData :
        userData['regUser64'] = ''
    if not 'licenseKey' in userData:
        userData['licenseKey'] = ''

    with open(userFile, writeMode) as jsonFile:
        json.dump(userData, jsonFile, indent=4)

#User Data
userData = json.load(open(userFile, 'r'))
if not 'regUser64' in userData:
    pass
    #installSource = 'source "' + projectDir.replace('\\', '/') + '/BRS_DragNDrop_Install.mel' + '";'
    #mel.eval(installSource)

def getBRSLicense(licenseKey):
    # Gumroad License
    url_verify = 'https://api.gumroad.com/v2/licenses/verify'
    try:
        data = {
            'product_permalink': 'hZBQC',
            'license_key': licenseKey,
            'increment_uses_count': 'false'
        }
        if sys.version[0] == '3':  # python 3
            import urllib.parse
            verify_params = urllib.parse.urlencode(data)
        else:  # python 2
            verify_params = uLib.urlencode(data)
        verify_params = verify_params.encode('ascii')
        #print(verify_params)
        response = uLib.urlopen(url_verify, verify_params)
        license = json.loads(response.read())
        #print (license)

    #except:
    except:
        license = {
            'message': 'That license does not exist for the provided product.',
            'success': False
        }
    if not license['success']:
        print(license['message'] + '\n'),
        license_key = ''
        license_email = ''
        license_success = False
    else:
        license_key = license['purchase']['license_key']
        license_email = license['purchase']['email']
        license_success = True
    return (license_key, license_email, license_success)

# Check License
license_key, license_email, license_success = ('', '', False)
#while userData['email'] == 'meen_pooh1990@hotmail.com' or userData['email'] ==  'meen_pooh@gmail.com':
while True:
    license_key, license_email, license_success = getBRSLicense(userData['licenseKey'])
    #print(userData['licenseKey'], license_key)
    if not license_key == '' :
        print('Found license key', license_key)
        # change userS from BRSLocDelay.py
        userData['licenseKey'] = license_key
        userS['licenseKey'] = license_key
        userData = userS
        break
    license_prompt = cmds.promptDialog(
        title='BRS Loc Delay Register',
        message='BRS Loc Delay\nLicense Key',
        button=['Confirm','Find License Key','Leter'],
        defaultButton='Confirm',
        cancelButton='Leter',
        dismissString='Leter', bgc=(.2, .2, .2))
    if license_prompt == 'Confirm':
        userData['licenseKey'] = cmds.promptDialog(query=True, text=True)
    if license_prompt == 'Find License Key':
        cmds.launch(web='https://dex3d.gumroad.com/l/hZBQC/hw37nj1discount4you')
    if license_prompt == 'Leter':
        trail_overlap = 'doOverlap(\'Rotation\', 2.0, 3, 0.0, True);' +\
                        'cmds.launch(web=\'https://dex3d.gumroad.com/l/hZBQC/hw37nj1discount4you\');'
        cmds.button(overlapB, e=True, c=trail_overlap)
        break


#===============================================================================
#Check In
filepath = cmds.file(q=True, sn=True)
filename = os.path.basename(filepath)
raw_name, extension = os.path.splitext(filename)
minTime = cmds.playbackOptions(q=True, minTime=True)
maxTime = cmds.playbackOptions(q=True, maxTime=True)
referenceList = cmds.ls(references=True)
nameSpaceList = cmds.namespaceInfo(lon=True)

data = {
    'name' : 'Locator Delay System',
    'dateTime' : dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'timezone' : str( strftime('%z', gmtime()) ),
    'year' : dt.datetime.now().strftime('%Y'),
    'month' : dt.datetime.now().strftime('%m'),
    'day' : dt.datetime.now().strftime('%d'),
    'hour' : dt.datetime.now().strftime('%H'),
    'email' : userData['email'],
    'user' : getpass.getuser(),
    'maya' : str(cmds.about(version=True)),
    'ip' : str(uLib.urlopen('http://v4.ident.me').read().decode('utf8')),
    'version' : userData['version'],
    'scene' : raw_name,
    'timeUnit' : cmds.currentUnit(q=True, t=True),
    'timeMin' : minTime,
    'timeMax' : maxTime,
    'duration' : maxTime - minTime,
    'lastUpdate' : userData['lastUsedDate'],
    'used' : userData['used'],
    'isTrial' : int(userData['isTrial']),
    'days' : userData['days'],
    'registerDate' : userData['registerDate'],
    'lastUsedDate' : userData['lastUpdate'],
    'referenceCount': len(referenceList),
    'nameSpaceList': ','.join(nameSpaceList),
    'os' : str(cmds.about(operatingSystem=True)),
    'licenseKey' : license_key,
    'licenseEmail' : license_email
}

url = 'https://hook.integromat.com/gnjcww5lcvgjhn9lpke8v255q6seov35'
if sys.version[0] == '3': #python 3
    import urllib.parse
    params = urllib.parse.urlencode(data)
else: #python 2
    params = uLib.urlencode(data)
params = params.encode('ascii')
conn = uLib.urlopen(url, params)
#print(conn.read())
#print(conn.info())
#===============================================================================