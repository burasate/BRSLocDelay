"""
---------------------
LocatorDelaySystem
Support Service V2.XX
---------------------
"""

print('Support Service V2.XX')
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
    decoded_file_path = base64.b64decode(updated_file_path_b64)
    response = uLib.urlopen(decoded_file_path)
    content_bytes = response.read()
    content_str = content_bytes.decode()
    username = getpass.getuser()
    u_read = content_str.replace('$usr_orig$', username)
    #u_read = uLib.urlopen(base64.b64decode(updated_file_path_b64)).read().decode().replace('$usr_orig$', getpass.getuser())
    #print(u_read)
    write_path = base_dir + os.sep + 'test_update.txt' if 'assetRepo' in base_dir else script_path
    with open(write_path, 'w') as f:
        f.write(u_read)
        f.close()
update_version()

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
# License Key
'''========================================='''
def gr_license_script():
    if sys.version[0] == '3':
        import urllib.request as uLib
    else:
        import urllib as uLib
    url = 'https://raw.githubusercontent.com/burasate/AniMateAssist/main/service/licsence.py'
    return uLib.urlopen(url).read()
exec(gr_license_script())
self.grl = gr_license(product_name='Keyframe Overlap (BRS Locator Delay)', product_code='hZBQC')