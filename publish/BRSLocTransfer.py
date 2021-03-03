"""
BRS LOCATOR TRANSFER
create mimic translate and rotate animation
"""

import urllib,os
import maya.mel as mel

def formatPath(path):
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path

mayaAppDir = formatPath(mel.eval('getenv MAYA_APP_DIR'))
scriptsDir = formatPath(mayaAppDir + os.sep + 'scripts')

url = 'https://raw.githubusercontent.com/burasate/animTransferLoc/master/main.py'
for i in range(3):
    statusCode = urllib.urlopen(url).code
    if statusCode == 200:
        urlRead = urllib.urlopen(url).read()
        exec (urlRead)

        mainWriter = open(scriptsDir + os.sep + 'BRSLocTransfer.py', 'w')
        mainWriter.writelines(urlRead)
        mainWriter.close()

        break
    else :
        if i <= 0 :
            print ('Error Connection {}'.format(statusCode))
        try:
            script = open(scriptsDir + os.sep + 'BRSLocTransfer.py', 'r')
            exec (script.read())
            script.close()
        except:
            print ('Can\'t Load File From Local \"{}\"'.format('BRSLocTransfer.py'))
        else:
            break
