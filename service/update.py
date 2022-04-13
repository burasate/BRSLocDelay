"""
LOCATOR DELAY SYSTEM UPDATER
"""
from maya import cmds
from maya import mel
import os, json, urllib, getpass
import datetime as dt


def formatPath(path):
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path


mayaAppDir = formatPath(mel.eval('getenv MAYA_APP_DIR'))
scriptsDir = formatPath(mayaAppDir + os.sep + 'scripts')
projectDir = formatPath(scriptsDir + os.sep + 'BRSLocDelay')
presetsDir = formatPath(projectDir + os.sep + 'presets')
userFile = formatPath(projectDir + os.sep + 'user')
configFile = formatPath(projectDir + os.sep + 'config.json')

# print ('mayaAppDir = ' + mayaAppDir)
# print ('scriptsDir = ' + scriptsDir)
# print ('projectDir = ' + projectDir)
# print ('userSetupFile = ' + userFile)
# mayaAppDir = C:\Users\TEST\Documents\maya
# scriptsDir = C:\Users\TEST\Documents\maya\scripts
# projectDir = C:\Users\TEST\Documents\maya\scripts\BRSLocDelay
# userSetupFile = C:\Users\TEST\Documents\maya\scripts\BRSLocDelay\user

# Update
scriptUpdater = 'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/BRSLocDelaySystem.py'
urlReader = ''
mainReader = ''
try:
    mainReader = open(projectDir + os.sep + 'BRSLocDelaySystem.py', 'r').readlines()
except:
    cmds.confirmDialog(title='Update Failed',
                       message='Could not find \"BRSLocDelaySystem.py\"\nPlease make sure path is correct\n' + projectDir + os.sep,
                       button=['OK'])
else:
    mainReader = open(projectDir + os.sep + 'BRSLocDelaySystem.py', 'r').readlines()
    mainWriter = open(projectDir + os.sep + 'BRSLocDelaySystem.py', 'w')
    try:
        urlReader = urllib.urlopen(scriptUpdater).readlines()
        mainWriter.writelines(urlReader)
        mainWriter.close()
        print('Update Successful')
        # cmds.confirmDialog(title='BRS LOCATOR DELAY UPDATE', message='Update Successful', button=['OK'])
    except:
        mainWriter.writelines(mainReader)
        mainWriter.close()
        print('Update Failed')
        cmds.confirmDialog(title='Update Failed',
                           message='Could not find \"BRSLocDelaySystem.py\"\nPlease make sure path is correct\n' + projectDir + os.sep,
                           button=['OK'])

# -------------------------
# Supporter Coding For 110 - 114
# -------------------------
#"""
# Presets
try:
    os.mkdir(presetsDir)
except:
    pass

# Defualt Preset
DefualtS = {}
try:
    with open(presetsDir + os.sep + 'Defualt.json', 'r') as jsonFile:
        DefualtS = json.load(jsonFile)
except:
    DefualtS = {
        "aimY": True,
        "aimX": False,
        "aimZ": False,
        "posXZ": False,
        "lastSelection": [],
        "frameRate": 24,
        "aimInvert": False,
        "posXYZ": True,
        "locOffset": 0.0,
        "posY": False,
        "locDistance": 2.0,
        "locDynamic": 3,
        "smoothness": True,
        "isMode": "Rotation"
    }
    with open(presetsDir + os.sep + 'Defualt.json', 'wb') as jsonFile:
        json.dump(DefualtS, jsonFile, indent=4)


# User
try:
    with open(userFile, 'r') as f:
        userS = json.load(f)
except:
    pass
else:
    today = str(dt.date.today())
    userS['lastUsedDate'] = today
    todayDate = dt.datetime.strptime(userS['lastUsedDate'], '%Y-%m-%d')
    try:
        regDate = dt.datetime.strptime(userS['registerDate'], '%Y-%m-%d')
    except:
        regDate = dt.datetime.strptime(today, '%Y-%m-%d')
    userS['used'] = userS['used']
    userS['version'] = 1.17
    userS['days'] = abs((regDate - todayDate).days)
    userS['lastUpdate'] = today

    # M2A Support
    #user = str(getpass.getuser()).upper()
    #if user == 'PETE2':
        #userS['email'] = 'pete2@m2animation.com'

    with open(userFile, 'wb') as jsonFile:
        json.dump(userS, jsonFile, indent=4)

# Config
configS = {}
try:
    with open(configFile, 'r') as jsonFile:
        configS = json.load(jsonFile)
except:
    configS = {
        'aimX': False,
        'aimY': True,
        'aimZ': False,
        'aimInvert': False,
        'posXZ': False,
        'posY': False,
        'posXYZ': True,
        'frameRate': 24,
        'lastSelection': [],
        'locDistance': 2.0,
        'locDynamic': 3,
        'locOffset': 0.0,
        'smoothness': True,
        'isMode': 'Rotation',
    }
    with open(configFile, 'wb') as jsonFile:
        json.dump(configS, jsonFile, indent=4)
#"""

# .pyc Removal
pycList = [projectDir + os.sep + 'BRSLocDelaySystem.pyc', projectDir + os.sep + '__init__.pyc']
for pycF in pycList:
    try:
        os.remove(pycF)
    except:
        pass

# Finish
cmds.inViewMessage(amg='BRS Delay : Update <hl>Successful</hl>', pos='botCenter', fade=True,
                   fit=250, fst=2000, fot=250)
