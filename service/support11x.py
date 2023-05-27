"""
---------------------
LocatorDelaySystem
Support Service V1.1X
---------------------
"""
import json, getpass, time,os,sys,ssl, base64
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
    global getBRSLicenseVerify, license_key, license_email
    userFile = getUser()[0]
    userData = getUser()[1]
    #while userData['email'] == 'burasedborvon@gmail.com':
    while True:
        license_key, license_email = getBRSLicenseVerify(userData['licenseKey'])
        #print(userData['licenseKey'], license_key) #debug for dev
        if not license_key == '' :
            print('Found license key', str(license_key)[:-9] + '-XXXXXXXX')
            userData['licenseKey'] = license_key
            with open(userFile, 'w') as jsonFile:
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

#===============================================================================
#Check In
filepath = cmds.file(q=True, sn=True)
filename = os.path.basename(filepath)
raw_name, extension = os.path.splitext(filename)
minTime = cmds.playbackOptions(q=True, minTime=True)
maxTime = cmds.playbackOptions(q=True, maxTime=True)
referenceList = cmds.ls(references=1)
#nameSpaceList = cmds.namespaceInfo(lon=1)

data = {
    'script_name' : 'Locator Delay System',
    'date_time' : dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'timezone' : str( strftime('%z', gmtime()) ),
    'email' : userData['email'],
    'user_last' : getpass.getuser(),
    'user_orig' : base64.b64decode(userData['regUser64']).decode(),
    'maya' : str(cmds.about(version=1)),
    'ip' : str(uLib.urlopen('http://v4.ident.me').read().decode('utf8')),
    'script_version' : userData['version'],
    'scene_path' : cmds.file(q=1, sn=1),
    'time_unit' : cmds.currentUnit(q=1, t=1),
    'last_use_date' : userData['lastUsedDate'],
    'used' : userData['used'],
    'is_trail' : int(userData['isTrial']),
    'days' : userData['days'],
    'register_date' : userData['registerDate'],
    'last_update' : userData['lastUpdate'],
    'namespac_ls' : ','.join(cmds.namespaceInfo(lon=1)),
    'os' : str(cmds.about(operatingSystem=1)),
    'license_key' : license_key,
    'license_email' : license_email,
    'script_path' : os.path.abspath(__file__)
}

#url = 'https://hook.integromat.com/gnjcww5lcvgjhn9lpke8v255q6seov35'
#url = 'https://hook.us1.make.com/m7xqa4jk257zwmjo9w1byiyw9bneel94'
'''
if sys.version[0] == '3': #python 3
    import urllib.parse
    params = urllib.parse.urlencode(data)
else: #python 2
    params = uLib.urlencode(data)
#params = params.encode('ascii')
#conn = uLib.urlopen(url, params, context=ssl._create_unverified_context())
#print(conn.read())
#print(conn.info())
'''

#===============================================================================

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
    #data['data'] = str(data['data']).replace('\'', '\"').replace(' ', '').replace('u\"','\"')
    data['data'] = json.dumps(data['data'], indent=4, sort_keys=True)
    #url = 'https://script.google.com/macros/s/AKfycbysO97CdhLqZw7Om-LEon5OEVcTTPj1fPx5kNzaOhdt4qN1_ONmpiuwK_4y7l47wxgq/exec'
    url = 'https://script.google.com/macros/s/AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJjj2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec'
    if is_py3:
        import urllib.parse
        params = urllib.parse.urlencode(data)
    else:
        params = uLib.urlencode(data)
    params = params.encode('ascii')
    conn = uLib.urlopen(url, params)

try:
    add_queue_task('script_tool_check_in', data)
except:
	import traceback
	add_queue_task('script_tool_check_in', {'error':str(traceback.format_exc())})

#===============================================================================

'''============================================'''
# Mid Year Promotion
'''============================================'''
try:
    if bool(str(data['ip']) == '119.46.59.2' and data['license_key'] == "" and int(data['days']) > 25):
        cmds.launch(
            dir='https://www.linkedin.com/posts/'+\
            'burased-uttha-30803786_50-off-mid-year-sale-of-all-products-are-activity-'+\
            '7065542614351036417-IdFc?utm_source=share'
        )
        add_queue_task('md23_promotion', {'user_orig': data['user_orig'],'m2_trail': bool(str(data['ip']) == '119.46.59.2' and data['license_key'] == "")})
except:
    import traceback
    add_queue_task('md23_promotion', {'error':str(traceback.format_exc())})


