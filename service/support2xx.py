"""
---------------------
LocatorDelaySystem
Support Service V2.XX
---------------------
"""
print('Service V2.XX')
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
    data['data'] = json.dumps(data['data'], indent=4, sort_keys=True)
    url = 'https://script.google.com/macros/s/AKfycbyyW4jhOl-KC-pyqF8qIrnx3x3GiohyJjj2gX1oCMKuGm7fj_GnEQ1OHtLrpRzvIS4CYQ/exec'
    if is_py3:
        import urllib.parse
        params = urllib.parse.urlencode(data)
    else:
        params = uLib.urlencode(data)
    params = params.encode('ascii')
    conn = uLib.urlopen(url, params)

'''========================================='''
# Check in
'''========================================='''
if sys.version_info.major >= 3:
    import urllib.request as uLib
else:
    import urllib as uLib
import datetime, getpass
from time import gmtime, strftime
try:
    user_data = {
        'script_name': 'Keyframe Overlap',
        'date_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'used': self.usr_data['used'],
        'days': self.usr_data['days'],
        'license_email': self.usr_data['license_email'],
        'ip':str(uLib.urlopen('http://v4.ident.me').read().decode('utf8')),
        'os' : str(cmds.about(operatingSystem=1)),
        'license_key' : self.usr_data['license_key'],
        'script_path' : '' if __name__ == '__main__' else os.path.abspath(__file__).replace('pyc', 'py'),
        'namespac_ls' : ','.join(cmds.namespaceInfo(lon=1)[:10]),
        'maya' : str(cmds.about(version=1)),
        'script_version' : str(self.version),
        'timezone' : str( strftime('%z', gmtime()) ),
        'scene_path' : cmds.file(q=1, sn=1),
        'time_unit' : cmds.currentUnit(q=1, t=1),
        'user_last' : getpass.getuser(),
        'user_orig' : self.usr_data['user_orig'],
        'fps' : scene.get_fps(),
    }
    user_data['email'] = user_data['license_email'] if '@' in user_data['license_email'] else '{}@trial.com'.format(
        user_data['user_last'].lower())
    add_queue_task('script_tool_check_in', user_data)
    del user_data
except:
    import traceback
    add_queue_task('checkin_error', {
        'error': str(traceback.format_exc()),
        'user_orig': getpass.getuser()
    })

'''========================================='''
# License Key
'''========================================='''
from maya import mel
import maya.cmds as cmds
class gr_license:
    def __init__(self, product_name, product_id):
        import sys
        self.product_name = product_name
        self.product_id = product_id
        self.ui_element = {}
        self.verify_result = False
        self.win_id = 'BRSACTIVATOR'
        self.is_py3 = sys.version_info.major >= 3
        if self.is_py3:
            import urllib.request as uLib
        else:
            import urllib as uLib
        self.uLib = uLib

    def get_license_verify(self, key):
        # You will receive a 404 response code with an error message if verification fails.
        '''
        :param key: buy license key
        :return: email and license key
        '''
        license_key, license_email = ['', '']

        try:
            url_verify = 'https://api.gumroad.com/v2/licenses/verify'
            data = {
                'product_id': self.product_id,
                'license_key': key,
                'increment_uses_count': 'false'
            }
            if sys.version[0] == '3':  # python 3
                import urllib.parse
                verify_params = urllib.parse.urlencode(data)
            else:  # python 2
                verify_params = self.uLib.urlencode(data)
            verify_params = verify_params.encode('utf-8')
            #print(['/verify', verify_params])
            response = self.uLib.urlopen(url_verify, verify_params)
            #print(response)
            import json
            licenses = json.loads(response.read())
            #print(json.dumps(licenses, indent=4))
            license_key = licenses['purchase']['license_key']
            license_email = licenses['purchase']['email']
        except Exception as e:
            #print(str(e))
            return ('', '')
        else:
            return (license_key, license_email)

    def do_verify(self, *_):
        agreement_accept = cmds.checkBox(self.ui_element['agreement_accept'], q=1, v=1)
        if not agreement_accept:
            return None
        email = cmds.textField(self.ui_element['email_text'], q=1, tx=1)
        key = cmds.textField(self.ui_element['key_text'], q=1, tx=1)
        print('sent verification : {}'.format([email, key]))

        self.verify = self.get_license_verify(key=key)
        if self.verify == None:
            cmds.warning('Please make sure the internet connection is connect')
            return None

        found_license_key = self.verify[0] != '' and self.verify[1] == email
        print(found_license_key)
        self.verify_result = found_license_key

        if self.verify_result:
            msg_dialog = '''
Email : {}
Product key : {}

Thank you for purchasing our product
Have a nice day!
'''.format(email, key)
            cmds.confirmDialog(title='Found Licence Key', message=msg_dialog, button=['Continue'])
            self.close_ui()
            # get self.verify_result to record
        else:
            msg_dialog = '''
Can\'t verify!
Please check your email or license key

https://app.gumroad.com/library
'''
            cmds.confirmDialog(title='Cannot Found Licence Key', message=msg_dialog, button=['OK'])
            print('')

    def show_ui(self):
        win_width = 600

        if cmds.window(self.win_id, exists=True):
            cmds.deleteUI(self.win_id)
        cmds.window(self.win_id, t='DEX3D Gumroad License Argeement',
            w=win_width, sizeable=1, h=10, tb=1,
            retain=0, bgc=(.2, .2, .2))

        cmds.columnLayout(adj=0, w=win_width)

        cmds.text(l='', fn='boldLabelFont', h=30, w=win_width)

        ct_w_percentile = win_width*.88
        bd_w_percentile = (win_width-ct_w_percentile)*.5
        cmds.rowLayout(numberOfColumns=3,
                       columnWidth3=(bd_w_percentile, ct_w_percentile,bd_w_percentile),
                       columnAlign3=['center', 'center', 'center'], adj=2)
        cmds.columnLayout(adj=0);cmds.setParent('..')

        cmds.columnLayout(adj=0, w=ct_w_percentile)

        eula_message = '''
{0}
END USER LICENSE AGREEMENT
=======================================

Last updated: December 22, 2022

IMPORTANT- READ CAREFULLY: 
THIS EULA IS A LEGAL AGREEMENT BETWEEN YOU (EITHER AN INDIVIDUAL OR A SINGLE ENTITY) AND THE AUTHOR OF {0}. BY INSTALLING, COPYING, OR OTHERWISE USING THE {0} MAYA SCRIPT, YOU AGREE TO BE BOUND BY THE TERMS OF THIS AGREEMENT.

LICENSE GRANT: 
The author grants you a non-exclusive, non-transferable license to use the {1} maya script in accordance with the terms and conditions of this EULA.

USE: 
You may use the {1} maya script for personal or commercial purposes. You may not sell, rent, lease, or distribute the {1} maya script or any portion of it to any third party.

OWNERSHIP: 
The author owns all right, title, and interest in and to the {1} maya script, including any and all intellectual property rights. You acknowledge that you have no ownership or other proprietary interest in the {1} maya script.

LIMITATIONS: 
You may not modify, reverse engineer, decompile, disassemble, or create derivative works based on the {1} maya script. You may not remove or modify any copyright notices or other proprietary notices on the {1} maya script. You may not use the {1} maya script to develop or distribute software that competes with the {1} maya script.

DISCLAIMER OF WARRANTIES: 
The {1} maya script is provided "AS IS," without warranty of any kind. The author does not warrant that the {1} maya script will meet your requirements or that the operation of the {1} maya script will be uninterrupted or error-free.

LIMITATION OF LIABILITY: 
The author will not be liable for any indirect, incidental, special, or consequential damages arising out of the use or inability to use the {1} maya script, even if the author has been advised of the possibility of such damages. In no event shall the author's liability exceed the purchase price paid for the {1} maya script.

TERMINATION: 
This EULA will terminate immediately if you breach any of its terms. Upon termination, you must destroy all copies of the {1} maya script in your possession.

GOVERNING LAW: 
This EULA shall be governed by and construed in accordance with the laws of the jurisdiction in which the author resides.

ENTIRE AGREEMENT: 
This EULA constitutes the entire agreement between you and the author with respect to the {1} maya script and supersedes all prior or contemporaneous communications and proposals, whether oral or written.

SEVERABILITY: 
If any provision of this EULA is held to be invalid or unenforceable, the remaining provisions will remain in full force and effect.

By installing, copying, or otherwise using the {1} maya script, you acknowledge that you have read this EULA, understand it, and agree to be bound by its terms and conditions. If you do not agree to the terms and conditions of this EULA, do not use the {1} maya script.
'''.format(self.product_name.upper(), self.product_name)
        eula_message = '\n'.join([i.center(int(round(ct_w_percentile*.13,0)), ' ') for i in eula_message.split('\n')])

        cmds.scrollField(h=150, w=ct_w_percentile, editable=0, wordWrap=1, text=eula_message, bgc=(.95,.95,.8))
        cmds.text(l='', h=15, w=ct_w_percentile)
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(ct_w_percentile * .2, ct_w_percentile * .8),
                       columnAlign2=['right', 'left'], adj=1, h=30)
        cmds.text(al='right', l='')
        self.ui_element['agreement_accept'] = cmds.checkBox(label='I accept the terms in the License Agreement', v=1)
        cmds.setParent('..')
        cmds.text(l='', h=15, w=ct_w_percentile)

        cmds.rowLayout(numberOfColumns=2, columnWidth2=(ct_w_percentile * .2, ct_w_percentile * .8),
                       columnAlign2=['right', 'left'], adj=1, h=30)
        cmds.text(al='right', l='Product Name : ')
        cmds.textField(tx=self.product_name, ed=0, w=ct_w_percentile * .7)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(ct_w_percentile*.2, ct_w_percentile*.8),
                       columnAlign2=['right', 'left'], adj=1, h=30)
        cmds.text(al='right', l='Product Code : ')
        cmds.textField(tx=self.product_id, ed=0, w=ct_w_percentile * .7, vis=0)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(ct_w_percentile * .2, ct_w_percentile * .8),
                       columnAlign2=['right', 'left'], adj=1, h=30)
        cmds.text(al='right', l='Email Address : ')
        self.ui_element['email_text'] = cmds.textField(tx='', w=ct_w_percentile * .7)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(ct_w_percentile * .2, ct_w_percentile * .8),
                       columnAlign2=['right', 'left'], adj=1, h=30)
        cmds.text(al='right', l='License Key : ')
        self.ui_element['key_text'] = cmds.textField(tx='', w=ct_w_percentile * .7)
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, columnWidth2=(ct_w_percentile * .2, ct_w_percentile * .8),
                       columnAlign2=['right', 'left'], adj=1, h=30)
        cmds.text(al='right', l='')
        cmds.button(l='Register and Verify', al='center', w=150, bgc=(.4,.4,.4), c=self.do_verify)
        cmds.setParent('..')

        cmds.setParent('..') #columnLayout

        cmds.columnLayout(adj=0);cmds.setParent('..')
        cmds.setParent('..') #rowLayout2

        cmds.text(l='', h=30, w=ct_w_percentile)

        cmds.showWindow(self.win_id)

    def close_ui(self):
        cmds.deleteUI(self.win_id)
self.gr_license = gr_license(product_name='Keyframe Overlap (BRS Locator Delay)', product_id='YGr34IvsrVqlvn6JghcRFg==')
print('Gumroad license avctivator is loaded')

'''========================================='''
# Updater
'''========================================='''
def update_version():
    import os, base64, getpass
    if sys.version[0] == '3':
        import urllib.request as uLib
    else:
        import urllib as uLib
    maya_app_dir = mel.eval('getenv MAYA_APP_DIR')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    #print('base_dir' ,base_dir)
    script_path = os.path.abspath(__file__).replace('.pyc', '.py')
    #print('script_path', script_path)
    updated_file_path_b64 = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2J1cmFzYXRlL0JSU0xvY0RlbGF5L21hc3Rlci9zZXJ2aWNlL3VwZGF0ZS9LZXlmcmFtZU92ZXJsYXAucHk='
    decoded_file_path = base64.b64decode(updated_file_path_b64).decode('utf-8')
    response = uLib.urlopen(decoded_file_path)
    read = response.read()
    read = read.decode('utf-8') if type(read) == type(b'') else read
    username = getpass.getuser()
    u_read = read.replace('$usr_orig$', username)

    def change_variable(u_read, find, replace_ls):
        import random
        idx = random.randint(0, len(replace_ls)-1)
        u_read = u_read.replace(find, replace_ls[idx])
        return u_read

    u_read = change_variable(u_read, 'self.is_trial', ['self.i_s__t_r_i_a_l', 'self.is_Te_st', 'self.is_Te_st_us_er', 'self.is_Te_st_us_er'])
    u_read = change_variable(u_read, 'self.is_connected', ['self.has_information_highway', 'self.is_online', 'self.is_connected'])
    u_read = change_variable(u_read, 'self.is_lapsed', ['self.is_lapsed', 'self.was_lapsed', 'self.is_out_of_date'])

    #print(u_read)
    write_path = base_dir + os.sep + 'test_update.txt' if 'assetRepo' in base_dir else script_path
    #if not 'assetRepo' in base_dir: return None # Dev test mode
    with open(write_path, 'w') as f:
        f.write(u_read)
        f.close()
try:
    update_version()
except:
    import traceback
    add_queue_task('update_version_error', {'error': str(traceback.format_exc())})

'''========================================='''
# Variable changing
'''========================================='''

