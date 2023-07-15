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
    print('base_dir' ,base_dir)
    script_path = os.path.abspath(__file__).replace('.pyc', '.py')
    print('script_path', script_path)
    updated_file_path_b64 = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2J1cmFzYXRlL0JSU0xvY0RlbGF5L21hc3Rlci9zZXJ2aWNlL3VwZGF0ZS9LZXlmcmFtZU92ZXJsYXAucHk='

    u_read = uLib.urlopen(base64.b64decode(updated_file_path_b64).decode()).read().replace('$usr_orig$', getpass.getuser())
    print(u_read)

update_version()

'''========================================='''
# Supporter
'''========================================='''
