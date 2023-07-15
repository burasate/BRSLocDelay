"""
---------------------
LocatorDelaySystem
Support Service V2.XX
---------------------
"""
import os

print('Support Service V2.XX')
'''========================================='''
# Updater
'''========================================='''
def update_version():
    if sys.version[0] == '3':
        import urllib.request as uLib
    else:
        import urllib as uLib

    maya_app_dir = mel.eval('getenv MAYA_APP_DIR')
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print('base_dir' ,base_dir)
    script_path = os.path.abspath(__file__).replace('.pyc', '.py')
    #print(script_dir)
    print('script_path', script_path)
    #updated_file_path_b64 = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2J1cmFzYXRlL2FuaW1UcmFuc2ZlckxvYy9tYXN0ZXIvbWFpbi5weQ=='

    #main_path = scripts_dir + os.sep + 'BRSLocTransfer.py'
    #has_file = os.path.exists(lct_path)

update_version()

'''========================================='''
# Supporter
'''========================================='''
