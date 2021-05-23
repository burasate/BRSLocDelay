"""
BRS LOCATOR DELAY
easy ovelaping animation
"""

import urllib,os
import maya.mel as mel

def formatPath(path):
    path = path.replace("/", os.sep)
    path = path.replace("\\", os.sep)
    return path

mayaAppDir = formatPath(mel.eval('getenv MAYA_APP_DIR'))
scriptsDir = formatPath(mayaAppDir + os.sep + 'scripts')
projectDir = formatPath(scriptsDir + os.sep + 'BRSLocDelay')
locDelayFile = formatPath(projectDir + os.sep + 'BRSLocDelaySystem.py')

url = 'https://raw.githubusercontent.com/burasate/BRSLocDelay/master/BRSLocDelaySystem.py'
for i in range(3):
    statusCode = urllib.urlopen(url).code
    if statusCode == 200:
        urlRead = urllib.urlopen(url).read()
        mainWriter = open(locDelayFile, 'w')
        mainWriter.writelines(urlRead)
        mainWriter.close()

        script = open(locDelayFile, 'r')
        exec (script.read())
        showBRSUI()
        script.close()

        break
    else :
        if i <= 0 :
            print ('Error Connection {}'.format(statusCode))
        try:
            script = open(locDelayFile, 'r')
            exec (script.read())
            showBRSUI()
            script.close()
        except:
            print ('Can\'t Load File From Local \"{}\"'.format(locDelayFile))
        else:
            break