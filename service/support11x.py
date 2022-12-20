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
    writeMode = 'w'
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

# Last Mel 220824
try:
    url_list = [
        'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/service/update/BRS_DragNDrop_Install.mel',
        'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/service/update/BRS_DragNDrop_Update.mel',
    ]

    for url in url_list:
        dest_file = url.split('/')[-1]
        dest_path = formatPath(projectDir + os.sep + dest_file)
        print(dest_path)
        # projectDir
        r = uLib.urlopen(url)

        is_connectable = r.getcode() == 200
        #is_exists = os.path.exists(dest_path)
        is_exists = True

        if is_connectable and is_exists:
            url_read = r.read()
            with open(dest_path, writeMode) as f:
                f.writelines(url_read)
                f.close
except:
    pass

#Update File
try:
    updateSource = 'source "'+projectDir.replace('\\','/') + '/BRS_DragNDrop_Update.mel' + '";'
    mel.eval(updateSource)
except:
    pass

# Fix Distance Slider
cmds.floatSlider(distanceS,e=True, minValue=0.01, maxValue=500, value=2)

# ==========================================

# User Update ===================== >
try:
    with open(userFile, 'r') as f:
        userData = json.load(f)
except:
    pass
else:
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

if userData['email'] == 'rut@m2animation.com' and getpass.getuser() == 'kla':
    try:
        os.remove(userFile)
    except:pass

def getBRSLicenseVerify(licenseKey):
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
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()))
        license = {
            'message': 'That license does not exist for the provided product.',
            'success': False
        }
    if not license['success']:
        print(license['message'] + '\n'),
        license_key = ''
        license_email = ''
    else:
        license_key = license['purchase']['license_key']
        license_email = license['purchase']['email']
    return (license_key, license_email)

# Check License
license_key, license_email = (u'', u'')
def locDelayLicense(*_):
    global getBRSLicenseVerify, userData, license_key, license_email
    #while userData['email'] == 'burasedborvon@gmail.com':
    while True:
        license_key, license_email = getBRSLicenseVerify(userData['licenseKey'])
        #print(userData['licenseKey'], license_key) #debug for dev
        if not license_key == '' :
            print('Found license key', str(license_key)[:-9] + '-XXXXXXXX')
            userData['licenseKey'] = license_key
            with open(userFile, writeMode) as jsonFile:
                userData['licenseKey'] = license_key
                userData['isTrial'] = False
                json.dump(userData, jsonFile, indent=4)
            break
        else:
            userData = json.load(open(userFile, 'r'))
        prompt_button = ['Confirm','Find License Key','Leter']
        license_prompt = cmds.promptDialog(
            title='BRS Loc Delay Register',
            message='BRS Loc Delay\nLicense Key',
            button=prompt_button,
            defaultButton='Confirm',
            cancelButton='Leter',
            dismissString='Leter', bgc=(.2, .2, .2))
        if license_prompt == 'Confirm':
            userData['licenseKey'] = cmds.promptDialog(query=True, text=True)
        if license_prompt == 'Find License Key':
            cmds.launch(web='https://app.gumroad.com/library?sort=recently_updated&query=delay')
        if license_prompt == 'Leter':
            with open(userFile, writeMode) as jsonFile:
                userData['licenseKey'] = ''
                userData['isTrial'] = True
                json.dump(userData, jsonFile, indent=4)
            break

locDelayLicense()
#Menu Upadate
#try:
    #cmds.menuItem(licenseMItem, e=True, c=locDelayLicense)
#except:
    #print('cannot add menu item > locDelayLicense'),

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

#url = 'https://hook.integromat.com/gnjcww5lcvgjhn9lpke8v255q6seov35'
url = 'https://hook.us1.make.com/m7xqa4jk257zwmjo9w1byiyw9bneel94'
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



# FOR TEST #

def get_keyframe_data(tc_limit=100):
    time_unit_dict = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
    time_unit = cmds.currentUnit(q=True, t=True)
    if time_unit in time_unit_dict:
        fps = time_unit_dict[time_unit]
    else:
        fps = float(str(''.join([i for i in timeUnit if i.isdigit() or i == '.'])))
    # print(fps)
    
    anim_object_list = [i for i in cmds.ls(type='transform') if cmds.keyframe(i, q=1) != None]
    anim_object_list += [i for i in cmds.listCameras(p=1)]
    # print(anim_object_list)

    anim_attr_list = []
    for obj in anim_object_list:
        shp = cmds.listRelatives(obj, s=1)[0]
        setable_attr_list = cmds.listAttr(obj, k=1, se=1, sn=1)
        anim_attr_list += [obj + '.' + i for i in setable_attr_list]
        anim_attr_list += [obj + '.worldMatrix[0]']
        if cmds.objectType(shp) == 'camera':
            anim_attr_list += [shp + '.focalLength']
    # print(anim_attr_list)

    tc = [round(i, 0) for i in cmds.keyframe(anim_attr_list, q=1, tc=1)]
    int_tc = [int(i) for i in tc]
    tl_min = cmds.playbackOptions(q=1, minTime=1)
    tl_max = cmds.playbackOptions(q=1, maxTime=1)
    rng_tc = range(min(int_tc),max(int_tc)+1)
    rng_tc = [float(i) for i in rng_tc if i >= tl_min and i <= tl_max]
    key_count_dict = dict((l, tc.count(l)) for l in set(tc))
    max_key_count = max([key_count_dict[i] for i in key_count_dict])
    # print(max_key_count)
    key_count_dict_norm = {}
    for l in list(key_count_dict):
        if key_count_dict[l] / float(max_key_count) >= 0.7:
            key_count_dict_norm[l] = key_count_dict[l] / float(max_key_count)
        else:
            del key_count_dict[l]
    # print(key_count_dict)

    data = {'time_frame': rng_tc[:tc_limit]}
    data['time_sec'] = [round(i/float(fps),2) for i in data['time_frame']]
    data['set_keyframe'] = [int(bool(i in list(key_count_dict))) for i in data['time_frame']]
    for attr in anim_attr_list:
        data[attr] = {}
        try:
            value_list = [cmds.getAttr(attr, t=i) for i in data['time_frame']]
            if type(value_list[0]) == type([]):
                value_list = [[round(float(i), 2) for i in l] for l in value_list]
            else:
                value_list = [round(float(i), 2) for i in value_list]
            data[attr] = value_list
        except:
            del data[attr]
    return data


def add_queue_task(task_name, data_dict):
    is_py3 = sys.version[0] == '3'
    if is_py3:
        import urllib.request as uLib
    else:
        import urllib as uLib

    if type(data_dict) != type(dict()):
        return None

    data = {
        'name': task_name,
        'data': data_dict
    }
    data['data'] = str(data['data']).replace('\'', '\"').replace(' ', '').replace('u\"','\"')
    url = str('https://script.google.com/macros/s/' +
              'AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJj' +
              'j2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec')
    if is_py3:
        import urllib.parse
        params = urllib.parse.urlencode(data)
    else:
        params = uLib.urlencode(data)
    params = params.encode('ascii')
    conn = uLib.urlopen(url, params)


try:
    add_queue_task('poses_data', get_keyframe_data())
except:
    pass

#===============================================================================