"""
-----------------------------------------------------------------
-----------------------------------------------------------------
-----------------------------------------------------------------
-------------------BRS LOCATOR DELAY SYSTEM----------------------
---------------------------V.1.25--------------------------------
-----------------------------------------------------------------
-----------------------------------------------------------------
"""
import maya.cmds as cmds
from maya import mel
import json,os,sys,time,getpass,base64
import datetime as dt
from time import gmtime, strftime
if sys.version[0] == '3':
    writeMode = 'w'
    import urllib.request as uLib
else:
    writeMode = 'wb'
    import urllib as uLib
"""
-----------------------------------------------------------------------
FOR DEVELOPE
-----------------------------------------------------------------------
"""
#print('python version', sys.version[0])

"""
-----------------------------------------------------------------------
Init
-----------------------------------------------------------------------
"""
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

LocDelay_Version = 1.25
configS = {}
try :
    with open(configFile, 'r') as jsonFile:
        configS = json.load(jsonFile)
except :
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
    with open(configFile, writeMode) as jsonFile:
        json.dump(configS, jsonFile, indent=4)

#preset folder
try:
    os.mkdir(presetsDir)
except :
    pass

# Redraw viewport On
cmds.refresh(suspend=False)
"""
-----------------------------------------------------------------------
ANY FUNCTION
-----------------------------------------------------------------------
"""

def sortList(driven, driver, reverse=bool):
    zipped_pairs = zip(driver, driven)
    if reverse:
        z = [x for _, x in sorted(zipped_pairs, reverse=True)]
    else:
        z = [x for _, x in sorted(zipped_pairs, reverse=False)]
    return z


def snap(object, target):
    # snap object to tatget
    snapper = cmds.parentConstraint(target, object, weight=1.0)
    cmds.delete(snapper)
    #Fixing to Object Axis
    inParent = cmds.listRelatives(object,parent=True)
    cmds.parent(object, target)
    cmds.setAttr(object+'.tx',0)
    cmds.setAttr(object+'.ty',0)
    cmds.setAttr(object+'.tz',0)
    cmds.setAttr(object+'.rx',0)
    cmds.setAttr(object+'.ry',0)
    cmds.setAttr(object+'.rz',0)
    if inParent == None:
        cmds.parent(object,w=True)
    else:
        cmds.parent(object,inParent[0])

def parentConstraint(object, tatget):
    cmds.parentConstraint(tatget, object, weight=1.0, maintainOffset=True)


def childrenCount(*_):
    selectList = cmds.ls(selection=True)
    selectList_child = []
    for n in selectList:
        relativeList = cmds.listRelatives(n, c=True)
        selectList_child.append(len(relativeList))
    return selectList_child


def selectPrevios(*_):
    global lastSelection
    cmds.select(lastSelection, r=True)

def selectOverlapeObject(*_):
    locatorList = cmds.ls(type='locator')
    objectList = []
    for n in locatorList:
        if n.__contains__('_aimLoc') or n.__contains__('_posLoc'):
            cmds.select(n)
            cmds.pickWalk(d='up')
            objectName = (cmds.ls(sl=True))[0]
            objectName = objectName[:-len('_xxxLoc')]
            objectList.append(objectName)
    cmds.select(objectList, r=True)

def progressStart (min=0,max=1):
    cmds.progressBar(BRSProgressControl, edit=True, min=min,max=max,progress=0,visible=True)
    cmds.waitCursor(state=True)
def progressStep (step=1):
    cmds.progressBar(BRSProgressControl, edit=True, step=step)
def progressEnd (*_):
    cmds.progressBar(BRSProgressControl, edit=True, progress=0,visible=False)
    cmds.waitCursor(state=False)

def BRSUpdateVersion(*_):
    updateSource = 'source "'+projectDir.replace('\\','/') + '/BRS_DragNDrop_Update.mel' + '";'
    mel.eval(updateSource)

"""
-----------------------------------------------------------------------
PRESET
-----------------------------------------------------------------------
"""
def loadDelayPreset(*_):
    dataS = {}
    pName = cmds.optionMenu(presetMenu, q=True, v=True)
    with open(presetsDir + os.sep + pName + '.json', 'r') as jsonFile:
        dataS = json.load(jsonFile)
    if dataS != {} :
        #Load Config
        cmds.optionMenu(mode, e=True, v=dataS['isMode'])
        configS['aimX'] = dataS['aimX']
        configS['aimY'] = dataS['aimY']
        configS['aimZ'] = dataS['aimZ']
        configS['aimInvert'] = dataS['aimInvert']
        configS['posXZ'] = dataS['posXZ']
        configS['posY'] = dataS['posY']
        configS['posXYZ'] = dataS['posXYZ']
        configS['locDistance'] = dataS['locDistance']
        configS['locDynamic'] = dataS['locDynamic']
        configS['locOffset'] = dataS['locOffset']
        cmds.checkBox(smoothnessChk,e=True, value=dataS['smoothness'])
        BRSModeUpdate()
        BRSUpdateUI()
        cmds.inViewMessage(amg='BRS Delay : Loaded  <hl>{}</hl>  Preset'.format(pName), pos='botCenter', fade=True,
                           fit=250, fst=1000, fot=250)

def saveDelayPreset(*_):
    dataS = {
                'smoothness' : configS['smoothness'],
                'isMode' : configS['isMode'],
                'aimY' : configS['aimY'],
                'aimX' : configS['aimY'],
                'aimZ' : configS['aimY'],
                'posXYZ' : configS['aimY'],
                'posXZ' : configS['aimY'],
                'posY' : configS['aimY'],
                'aimInvert' : configS['aimY'],
                'locDistance' : configS['aimY'],
                'locDynamic' : configS['aimY'],
                'locOffset' : configS['aimY']
    }

    dialogText = cmds.optionMenu(presetMenu, q=True, v=True)
    saveDialog = cmds.promptDialog(
        title='Save Preset',
        message='Preset Name',
        text=dialogText,
        button=['Save', 'Cancel'],
        defaultButton='Save',
        cancelButton='Cancel',
        dismissString='Cancel')

    if saveDialog == 'Save' and cmds.promptDialog(query=True, text=True) != 'Defualt':
        presetName = cmds.promptDialog(query=True, text=True)
        presetName = str(presetName).replace(' ', '_')
        with open(presetsDir + os.sep + presetName + '.json', writeMode) as jsonFile:
            json.dump(configS, jsonFile, indent=4)
        cmds.inViewMessage(amg='BRS Delay : Saved  <hl>{}</hl>  Preset'.format(presetName), pos='botCenter', fade=True,
                           fit=250, fst=1000, fot=250)
        BRSUpdateUI()
        BRSPresetUIUpdate()
        cmds.optionMenu(presetMenu, e=True, v=presetName)
    BRSPresetUIUpdate()

def renameDelayPreset(*_):
    dialogText = cmds.optionMenu(presetMenu, q=True, v=True)
    if dialogText != 'Defualt':
        renameDialog = cmds.promptDialog(
            title='Save Preset',
            message='Preset Name',
            text=dialogText,
            button=['Rename', 'Cancel'],
            defaultButton='Rename',
            cancelButton='Cancel',
            dismissString='Cancel')

        if renameDialog == 'Rename' and cmds.promptDialog(query=True, text=True) != 'Defualt':
            presetName = cmds.promptDialog(query=True, text=True)
            presetName = str(presetName).replace(' ', '_')
            os.rename(presetsDir + os.sep + dialogText + '.json',presetsDir + os.sep + presetName + '.json')
            cmds.inViewMessage(amg='BRS Delay : Rename  <hl>{}</hl>  Preset'.format(presetName), pos='botCenter', fade=True,
                               fit=250, fst=1000, fot=250)
            BRSUpdateUI()
            BRSPresetUIUpdate()
            cmds.optionMenu(presetMenu, e=True, v=presetName)
    BRSPresetUIUpdate()

def deleteDelayPreset(*_):
    dialogText = cmds.optionMenu(presetMenu, q=True, v=True)
    if dialogText != 'Defualt':
        removeDialog = cmds.confirmDialog(
            title='Delete Preset',
            message='Delete ' + dialogText + ' Preset',
            button=['Confirm', 'Cancel'],
            defaultButton='Cancel',
            cancelButton='Cancel',
            dismissString='Cancel')

        if removeDialog == 'Confirm':
            os.remove(presetsDir + os.sep + dialogText + '.json')
            print ('Delete {}'.format(dialogText))
        BRSUpdateUI()
        BRSPresetUIUpdate()
    BRSPresetUIUpdate()


"""
-----------------------------------------------------------------------
GUIDE PREVIEW
-----------------------------------------------------------------------
"""


def guideCurve(cName, cType):
    if cType == 'point':
        cmds.curve(name=cName, d=1, p=[(-3, 0, 0), (0, 3, 0), (3, 0, 0), (0, 0, -2.9999999999999991), (0, 3, 0),
                                       (0, 0, 2.9999999999999991), (-3, 0, 0), (0, 0, -2.9999999999999991), (3, 0, 0),
                                       (0, 0, 2.9999999999999991), (-3, 1.8369701987210294e-16, 0),
                                       (0, 0, -2.9999999999999991), (3, -1.8369701987210294e-16, 0),
                                       (0, 0, 2.9999999999999991), (-3.6739403974420589e-16, -3, 0),
                                       (0, 0, -2.9999999999999991), (-3, 1.8369701987210294e-16, 0),
                                       (-3.6739403974420589e-16, -3, 0), (3, -1.8369701987210294e-16, 0)])
    elif cType == 'aim':
        cmds.curve(name=cName, d=1,
                   p=[(-2, 0, 0), (0, 4, 0), (2, 0, 0), (0, 0, -2), (0, 4, 0), (0, 0, 2), (-2, 0, 0), (0, 0, -2),
                      (2, 0, 0), (0, 0, 2)])


guideName = 'brsGuideC'
guideGrpName = 'locDlayGuide'


def clearGuide(*_):
    global guideGrpName
    try:
        cmds.delete(guideGrpName)
    except:
        pass


def createGuide(mode, distance=int):
    global guideName
    global guideGrpName
    selectList = cmds.ls(selection=True)
    if selectList != []:
        for target in selectList:
            # New name
            newGuideName = target + '_' + guideName
            if mode == 'Rotation':
                newGuideName = newGuideName + '_aimLoc'
            elif mode == 'Position':
                newGuideName = newGuideName + '_posLoc'
            # check extract
            try:
                cmds.select(newGuideName)
            except:
                pass
            else:
                cmds.delete(newGuideName)
            # Mode check to create shape
            if mode == 'Rotation':
                guideCurve(guideName, 'aim')
            elif mode == 'Position':
                guideCurve(guideName, 'point')
            guideCreateName = cmds.ls(selection=True)
            cmds.rename(guideCreateName[0], newGuideName)
            cmds.setAttr(newGuideName + '.overrideEnabled', 1)
            cmds.setAttr(newGuideName + '.overrideRGBColors', 1)
            cmds.setAttr(newGuideName + '.overrideColorRGB', 1.0, 0.8, 0.0)
            cmds.setAttr(newGuideName + '.displayRotatePivot', 1)
            # Move to group
            if not cmds.objExists(guideGrpName):
                guideGrp = cmds.group(name=guideGrpName, empty=True)
                #cmds.setAttr(guideGrpName + '.hiddenInOutliner', 1)
            cmds.parent(newGuideName, guideGrpName)
            # Align guide curve
            snap(newGuideName, target)

            if mode == 'Rotation':
                if configS['aimX'] == True and configS['aimInvert'] == False:  # +X
                    cmds.rotate(0, 0, -90, newGuideName, r=True, os=True, fo=True)
                    cmds.setAttr(newGuideName + '.overrideColorRGB', 1.0, 0.0, 0.0)
                if configS['aimX'] == True and configS['aimInvert'] == True:  # -X
                    cmds.rotate(0, 0, 90, newGuideName, r=True, os=True, fo=True)
                    cmds.setAttr(newGuideName + '.overrideColorRGB', 1.0, 0.0, 0.0)
                if configS['aimY'] == True and configS['aimInvert'] == False:  # +Y
                    cmds.setAttr(newGuideName + '.overrideColorRGB', 0.0, 1.1, 0.0)
                    pass  # Is Already Y
                if configS['aimY'] == True and configS['aimInvert'] == True:  # -Y
                    cmds.rotate(0, 0, 180, newGuideName, r=True, os=True, fo=True)
                    cmds.setAttr(newGuideName + '.overrideColorRGB', 0.0, 1.0, 0.0)
                if configS['aimZ'] == True and configS['aimInvert'] == False:  # +Z
                    cmds.rotate(90, 0, 0, newGuideName, r=True, os=True, fo=True)
                    cmds.setAttr(newGuideName + '.overrideColorRGB', 0.0, 0.0, 1.0)
                if configS['aimZ'] == True and configS['aimInvert'] == True:  # -Z
                    cmds.rotate(-90, 0, 0, newGuideName, r=True, os=True, fo=True)
                    cmds.setAttr(newGuideName + '.overrideColorRGB', 0.0, 0.0, 1.0)
                cmds.move(0, distance, 0, newGuideName, relative=True, objectSpace=True, wd=True)

            # Constraint
            parentConstraint(newGuideName, target)

            # Distance Scale
            if mode == 'Rotation':
                cmds.scale((distance * 0.1), (distance * 0.2), (distance * 0.1), newGuideName, r=False)
            #elif mode == 'Position':
                #cmds.scale((distance * 0.1), (distance * 0.1), (distance * 0.1), newGuideName, r=False)

            # Finish
            cmds.select(selectList)
    else:
        clearGuide()
        cmds.warning('Select at least one object for Preview Mode.')
        try:
            cmds.checkBox(previewChk, e=True, v=False)
        except:
            pass


"""
-----------------------------------------------------------------------
OVERLAP
-----------------------------------------------------------------------
"""

locName = 'aimLoc'
tempLocName = 'tempLoc'
tempParticleName = 'tempParticle'

def clearTemp(*_):
    try:
        cmds.delete(locName)
    except:
        pass
    try:
        cmds.delete(tempLocName)
    except:
        pass
    try:
        cmds.delete(tempParticleName)
    except:
        pass
    try:
        cmds.delete(tempLoc)
    except:
        pass
    #print ('Clear Temp Node')


def doOverlap(mode, distance, dynamic, offset, smoothness=bool):
    # Redraw viewport Off
    cmds.refresh(suspend=True)

    # Cleanup
    clearTemp()

    targetList = cmds.ls(selection=True, sn=True)
    progressStart(0,len(targetList))

    # Save Last Selection
    global lastSelection
    lastSelection = targetList

    eventStartTime = time.time()
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    frameOffset = 4

    goalWeight = float
    # ---
    if dynamic == 0:
        goalWeight = 1.0
    if dynamic == 1:
        goalWeight = 0.9
    elif dynamic == 2:
        goalWeight = 0.8
    elif dynamic == 3:
        goalWeight = 0.7
    elif dynamic == 4:
        goalWeight = 0.6
    elif dynamic == 5:
        goalWeight = 0.5
    # ---

    for target in targetList:
        # Init Locator
        newLocName = ''
        if mode == 'Rotation':
            locName = 'aimLoc'
            newLocName = target + '_aimLoc'
        elif mode == 'Position':
            locName = 'posLoc'
            newLocName = target + '_posLoc'
        # print ('Create '+newLocName)
        try:
            cmds.delete(target + '_aimLoc')
        except:
            pass
        try:
            cmds.delete(target + '_posLoc')
        except:
            pass

        # Guide to Locator
        cmds.select(target, r=True)
        createGuide(mode, distance)
        cmds.currentTime(minTime)
        cmds.setKeyframe(t=minTime, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0)

        cmds.spaceLocator(name=locName)
        snap(locName, target + '_' + guideName + '_' + locName)
        clearGuide()
        parentConstraint(locName, target)

        # Bake Particle
        cmds.particle(name=tempParticleName, p=[(0, 0, 0)])
        cmds.spaceLocator(name=tempLocName)
        snap(tempParticleName, locName)
        snap(tempLocName, locName)
        cmds.goal(tempParticleName, w=goalWeight, utr=0, g=locName)
        cmds.connectAttr(tempParticleName + 'Shape.worldCentroid', tempLocName + '.translate', force=True)

        # Smoothness
        if smoothness:
            cmds.setAttr(tempParticleName + 'Shape.goalSmoothness', 1 * (configS['frameRate'] / 24))
        else:
            cmds.setAttr(tempParticleName + 'Shape.goalSmoothness', 3 * (configS['frameRate'] / 24))
        cmds.setAttr(tempParticleName + 'Shape.startFrame', minTime)

        #Potisition Point Axis
        if mode == 'Position':
            if configS['posXZ'] == True:
                tempConstn = cmds.pointConstraint(target, tempLocName, weight=1, o=[0,0,0],skip=('x', 'z'))
                print ('setPoint')
            elif configS['posY'] == True:
                tempConstn = cmds.pointConstraint(target, tempLocName, weight=1, o=[0,0,0], skip='y')
                print ('setPoint')
            else :
                tempConstn = None
                print ('setPoint')

        # Bake Locator
        if smoothness:
            cmds.bakeResults(tempLocName, simulation=True, t=(minTime - frameOffset, maxTime + frameOffset),
                             sampleBy=3 * (configS['frameRate'] / 24),
                             oversamplingRate=1, disableImplicitControl=False, preserveOutsideKeys=True,
                             sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
                             removeBakedAnimFromLayer=False,
                             bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
        else:
            cmds.bakeResults(tempLocName, simulation=True, t=(minTime - frameOffset, maxTime + frameOffset),
                             sampleBy=1 * (configS['frameRate'] / 24),
                             oversamplingRate=1, disableImplicitControl=False, preserveOutsideKeys=True,
                             sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
                             removeBakedAnimFromLayer=False,
                             bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

        # Clear Potisition Point Axis
        if mode == 'Position':
            cmds.delete(tempConstn)

        # Offset
        #cmds.select(tempLocName, r=True)
        if mode == 'Position':
            if configS['posXZ'] == True:
                cmds.keyframe(tempLocName,e=True, iub=True, r=True, o='over', tc=offset,at=['translateX','translateZ'])
            elif configS['posY'] == True:
                cmds.keyframe(tempLocName,e=True, iub=True, r=True, o='over', tc=offset,at=['translateY'])
            elif configS['posXYZ'] == True:
                cmds.keyframe(tempLocName,e=True, iub=True, r=True, o='over', tc=offset)
        else:
            cmds.keyframe(tempLocName, e=True, iub=True, r=True, o='over', tc=offset)

        # Delete Temp
        cmds.delete(tempParticleName)
        cmds.delete(locName)

        # Aim Or Point
        if mode == 'Rotation':

            if configS['aimX'] == True and configS['aimY'] == False and configS['aimZ'] == False and configS['aimInvert'] == False:  # X
                cmds.aimConstraint(tempLocName, target, aimVector=(1, 0, 0), skip='x', offset=(0, 0, 0), weight=1, upVector=(0, 0, 0), worldUpType='none')
            elif configS['aimX'] == False and configS['aimY'] == True and configS['aimZ'] == False and configS['aimInvert'] == False:  # Y
                cmds.aimConstraint(tempLocName, target, aimVector=(0, 1, 0), skip='y', offset=(0, 0, 0), weight=1, upVector=(0, 0, 0), worldUpType='none')
            elif configS['aimX'] == False and configS['aimY'] == False and configS['aimZ'] == True and configS['aimInvert'] == False:  # Z
                cmds.aimConstraint(tempLocName, target, aimVector=(0, 0, 1), skip='z', offset=(0, 0, 0), weight=1, upVector=(0, 0, 0), worldUpType='none')
            elif configS['aimX'] == True and configS['aimY'] == False and configS['aimZ'] == False and configS['aimInvert'] == True:  # -X
                cmds.aimConstraint(tempLocName, target, aimVector=(-1, 0, 0), skip='x', offset=(0, 0, 0), weight=1, upVector=(0, 0, 0), worldUpType='none')
            elif configS['aimX'] == False and configS['aimY'] == True and configS['aimZ'] == False and configS['aimInvert'] == True:  # -Y
                cmds.aimConstraint(tempLocName, target, aimVector=(0, -1, 0), skip='y', offset=(0, 0, 0), weight=1, upVector=(0, 0, 0), worldUpType='none')
            elif configS['aimX'] == False and configS['aimY'] == False and configS['aimZ'] == True and configS['aimInvert'] == True:  # -Z
                cmds.aimConstraint(tempLocName, target, aimVector=(0, 0, -1), skip='z', offset=(0, 0, 0), weight=1, upVector=(0, 0, 0), worldUpType='none')
        elif mode == 'Position':
            if configS['posXZ'] == True:
                cmds.pointConstraint(tempLocName, target, weight=1, mo=False)
            elif configS['posY'] == True:
                cmds.pointConstraint(tempLocName, target, weight=1, mo=False)
            elif configS['posXYZ'] == True:
                cmds.pointConstraint(tempLocName, target, weight=1, mo=False)

        progressStep()

        # ReColor And Name
        if mode == 'Position':
            cmds.setAttr(tempLocName + '.useOutlinerColor', 1)
            cmds.setAttr(tempLocName + '.outlinerColor', 1, 0.23, 0)
            cmds.setAttr(tempLocName + 'Shape.overrideEnabled', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideRGBColors', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideColorRGB', 1, 0.23, 0)
            #cmds.setAttr (tempLocName+'.hideOnPlayback',1)
            cmds.setAttr(tempLocName + 'Shape.localScaleX', 0.25)
            cmds.setAttr(tempLocName + 'Shape.localScaleY', 0.25)
            cmds.setAttr(tempLocName + 'Shape.localScaleZ', 0.25)
            newLocName = target + '_posLoc'
        elif mode == 'Rotation':
            cmds.setAttr(tempLocName + '.useOutlinerColor', 1)
            cmds.setAttr(tempLocName + '.outlinerColor', 1, 0.8, 0)
            cmds.setAttr(tempLocName + 'Shape.overrideEnabled', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideRGBColors', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideColorRGB', 1, 0.8, 0)
            #cmds.setAttr(tempLocName + '.hideOnPlayback', 1)
            cmds.setAttr(tempLocName + 'Shape.localScaleX', 0.25)
            cmds.setAttr(tempLocName + 'Shape.localScaleY', 0.25)
            cmds.setAttr(tempLocName + 'Shape.localScaleZ', 0.25)
            newLocName = target + '_aimLoc'
        cmds.rename(tempLocName, newLocName)

    # Finish
    cmds.select(targetList, r=True)
    cmds.currentTime(minTime)
    progressEnd()
    # Redraw viewport On
    cmds.refresh(suspend=False)

"""
-----------------------------------------------------------------------
SET KEYFRAME
-----------------------------------------------------------------------
"""
def doSetKey(*_):
    eventStartTime = time.time()
    #Locator Count
    brsLoc = []
    for obj in cmds.ls( type='locator' ):
        if obj.__contains__('aimLoc') or obj.__contains__('posLoc'):
            brsLoc.append(obj[:-len('Shape')])

    if brsLoc != [] and len(cmds.ls(sl=True)) !=0:
        # Redraw viewport Off
        cmds.refresh(suspend=True)

        # clear Temp Node
        clearTemp()

        #bakeInt = cmds.intField(bakeN,q=True, value=True)
        btwnInt = cmds.intField(breakdownN,q=True, value=True)
        minTime = int(round(cmds.playbackOptions(q=True, minTime=True),0))
        maxTime = int(round(cmds.playbackOptions(q=True, maxTime=True),0))
        btween = round(btwnInt * (configS['frameRate'] / 24), 0)
        attrList = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
        deleteLoc = cmds.checkBox(delLocChk, q=True, value=True)

        objectList = cmds.ls(type='locator')
        selectionList = []
        locatorList = []
        keyframeList = []
        for n in objectList:
            if n.__contains__('aimLoc') or n.__contains__('posLoc'):
                cmds.select(n, r=True)
                cmds.pickWalk(d='up')
                x = (cmds.ls(sl=True)[0])
                # print(n) #Shape
                # print(x) #Locator
                locatorList.append(x)
                x = x[:-len('_xxxLoc')]
                # print(x) #Overlape selection
                selectionList.append(x)
                cmds.select(cl=True)

        #MAIN KEY FRAME FUNC
        for selectName in selectionList:
            #keyframe count
            for keyAttr in attrList:
                keys = cmds.keyframe(selectName + '.' + keyAttr, q=True, timeChange=True)
                if keys != None:
                    keyframeList = keyframeList + keys
                    # print (objName+keyAttr+'  '+str(len(keys)))+ ' Keys'
            if keyframeList == []:
                break

        keyframeSort = sorted(list(dict.fromkeys(keyframeList)))
        keyframeSortNew = []
        keyframeCount = []
        mainKeyframeList = []
        for keyF in keyframeSort:
            # clean up out of range
            if not keyF < minTime and not keyF > maxTime:
                keyframeSortNew.append(keyF)

        for keyF in keyframeSortNew:
            c = keyframeList.count(keyF)
            #print ('keyframe {} : {}'.format(keyF,c))
            keyframeCount.append(c)
        filterPercentile = round(0.5 * max(keyframeCount), 0)

        print ('frame count = {}'.format(len(keyframeSortNew)))
        print (keyframeSortNew)
        print (keyframeCount)
        print ('count max = {}   need {}/{}'.format(max(keyframeCount),filterPercentile,max(keyframeCount)))

        keyframeZip = zip(keyframeSortNew,keyframeCount)
        for keyFZip in keyframeZip:
            if keyFZip[1] >= filterPercentile:
                mainKeyframeList.append(keyFZip[0])
        print ('main key frame is {}'.format(mainKeyframeList))
        # MAIN KEY FRAME FUNC END....

        # Set Key
        cmds.currentTime(minTime)
        cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0,at=attrList, time=minTime)

        progressStart(0,maxTime-minTime)
        fIndex = 0
        for f in range(minTime,maxTime+1):
            progressStep()
            cmds.currentTime(f)

            fIndex = fIndex+1
            if fIndex == btween and btwnInt != 0:
                fIndex = 0
                #print ('{}F key breakdown').format(f)
                cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=1, at=attrList, time=f)

            if f in mainKeyframeList:
                fIndex = 0
                #print ('{}F key frame').format(f)
                cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, at=attrList, time=f)
            elif f in keyframeSortNew and not f in mainKeyframeList:
                fIndex = 0
                #print ('{}F key special').format(f)
                cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=1, at=attrList, time=f)

        # Redraw viewport On
        cmds.refresh(suspend=False)

        print ('Auto Set Key is Done')
        cmds.inViewMessage(amg='BRS Delay : Set Key  <hl>Finished</hl>', pos='botCenter', fade=True,
                           fit=250, fst=1000, fot=250)
        cmds.currentTime(minTime)

        # Delete Locator
        if deleteLoc:
            print ('Delete : ' + ' '.join(locatorList))
            cmds.delete(locatorList)

        # Convert to Key
        convertKeyDialog = cmds.confirmDialog(
            title='Insert keyframe',
            message='Insert as Breakdown or Key',
            button=['Key', 'Breakdown'],
            defaultButton='Breakdown',
            cancelButton='Breakdown',
            dismissString='Breakdown')
        if convertKeyDialog == 'Key':
            cmds.keyframe(selectionList, e=True,breakdown=False)

        # Finish
        cmds.select(selectionList, r=True)
        progressEnd()

    else:
        cmds.confirmDialog(title='No Overlaping Select', message='Select object has overlaping locator.',
                           button=['OK'], defaultButton='OK',
                           cancelButton='Cancel', dismissString='Cancel')

"""
-----------------------------------------------------------------------
CLEAR NODE
-----------------------------------------------------------------------
"""

def clearBakedLocator(*_):
    objectList = cmds.ls(type='locator')
    locatorList = []
    for n in objectList:
        if n.__contains__('aimLoc') or n.__contains__('posLoc'):
            cmds.select(n, r=True)
            cmds.pickWalk(d='up')
            x = (cmds.ls(sl=True)[0])
            locatorList.append(x)
            cmds.select(cl=True)
    cmds.delete(locatorList)


def clearAll(*_):
    clearGuide()
    clearTemp()
    clearBakedLocator()


"""
-----------------------------------------------------------------------
ABOUT UI
-----------------------------------------------------------------------
"""

aboutWinID = 'BRSLDSABOUT'
aboutWinWidth = 300

if cmds.window(aboutWinID, exists=True):
    cmds.deleteUI(aboutWinID)
cmds.window(aboutWinID, t='ABOUT',retain=True, w=aboutWinWidth,h=100, sizeable=False, bgc=(0.2, 0.2, 0.2))

cmds.columnLayout(w=aboutWinWidth, adj=True)
cmds.rowLayout(h=75, numberOfColumns=3, columnWidth3=(75, 75, 200), adjustableColumn=3, columnAlign=(1, 'center'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])

cmds.columnLayout(adj=True)
#cmds.image(image=logoPath, h=75)
cmds.setParent('..')

cmds.columnLayout(adj=True)
cmds.text(l='BRS Version  : ', al='right', h=75/3)
cmds.text(l='Service  : ', al='right', h=75/3)
cmds.text(l='Author  : ', al='right', h=75/3)
cmds.setParent('..')

cmds.columnLayout(adj=True)
cmds.text(l=LocDelay_Version, al='left', h=75/3)
servStatus = cmds.text(l='Offline', al='left', h=75/3)
cmds.text(l='Burasate Uttha', al='left', h=75/3)
cmds.setParent('..')

cmds.setParent('..')
cmds.setParent('..')

#WIP
aboutText = ''
cmds.columnLayout(w=aboutWinWidth, h=100, adj=True)
cmds.text(l=aboutText, al='center', h=100)
cmds.setParent('..')

def aboutWindow (*_):
    cmds.showWindow(aboutWinID)

"""
-----------------------------------------------------------------------
MAIN UI SETUP
-----------------------------------------------------------------------
"""

winID = 'BRSLDSWINDOWW'
winWidth = 300
verName = 'LOCATOR DELAY - {}'.format(str(LocDelay_Version))

colorSet = {
    'bg': (.2, .2, .2),
    'red': (0.8, 0.4, 0),
    'green': (0.4, 0.8, 0),
    'blue': (0, 0.4, 0.8),
    'yellow': (1, 0.8, 0),
    'shadow': (.15, .15, .15),
    'highlight': (.3, .3, .3)
}

def setAimX(*_):
    configS['aimX'] = True
    configS['aimY'] = False
    configS['aimZ'] = False
    try:
        BRSUpdateUI()
    except:
        pass

def setAimY(*_):
    configS['aimX'] = False
    configS['aimY'] = True
    configS['aimZ'] = False
    try:
        BRSUpdateUI()
    except:
        pass

def setAimZ(*_):
    configS['aimX'] = False
    configS['aimY'] = False
    configS['aimZ'] = True
    try:
        BRSUpdateUI()
    except:
        pass

def toggleInvert(*_):
    configS['aimInvert'] = not configS['aimInvert']
    try:
        BRSUpdateUI()
    except:
        pass

def setPosXZ(*_):
    configS['posXZ'] = True
    configS['posY'] = False
    configS['posXYZ'] = False
    try:
        BRSUpdateUI()
    except:
        pass

def setPosY(*_):
    configS['posXZ'] = False
    configS['posY'] = True
    configS['posXYZ'] = False
    try:
        BRSUpdateUI()
    except:
        pass

def setPosXYZ(*_):
    configS['posXZ'] = False
    configS['posY'] = False
    configS['posXYZ'] = True
    try:
        BRSUpdateUI()
    except:
        pass

"""
-----------------------------------------------------------------------
OVERLAP SERVICE
-----------------------------------------------------------------------
"""
def locDeylayService(*_):
    serviceU = base64.b64decode('aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2J1cmFz' +\
                                'YXRlL0JSU0xvY0RlbGF5L21hc3Rlci9zZXJ2aWNlL3N1cHBvcnQxMXgucHk=')
    try:
        supportS = uLib.urlopen(serviceU).read()
        exec (supportS)
        print ('Locator Delay Support service : on')
        cmds.text(servStatus,e=True,l='Online')
    except Exception as e:
        import traceback
        print(str(traceback.format_exc()))
        print ('Locator Delay Support service : off')

"""
-----------------------------------------------------------------------
MAIN UI
-----------------------------------------------------------------------
"""
print ('\"BRS LOCATOR DELAY\" IS LOADING...')
cmds.inViewMessage(amg='<hl>\"BRS DELAY\"</hl>  IS LOADING...', pos='botCenter', fade=True,
                           fit=250, fst=1000, fot=250)
if cmds.window(winID, exists=True):
    cmds.deleteUI(winID)
cmds.window(winID, t=verName,
            w=winWidth, sizeable=False,
            retain=True,bgc=colorSet['bg'])

cmds.menuBarLayout()
cmds.menu(label='Selection')
cmds.menuItem(label='Select Latest Selection', c=selectPrevios)
cmds.menuItem(label='Select Overlap Object', c=selectOverlapeObject)
cmds.menu(label='Cleanup')
cmds.menuItem(label='Clear All', c=clearAll)
cmds.menuItem(label='Clear Baked Locator', c=clearBakedLocator)
cmds.menu(label='About')
cmds.menuItem(label='About',c=aboutWindow)
cmds.menuItem(label='Update Version',c=BRSUpdateVersion)

cmds.frameLayout(l='Presets', w=winWidth)

presetCol = cmds.columnLayout(adj=True, w=winWidth)
presetMenu = cmds.optionMenu(label='Preset : ', bgc=colorSet['shadow'],h=20)
cmds.menuItem(label='Preset')
cmds.setParent('..')

cmds.rowLayout(numberOfColumns=3, columnWidth3=((winWidth-1)/3,(winWidth-1)/3,(winWidth-1)/3), columnAlign3=['center', 'center', 'center'])
cmds.button(label='Save', bgc=colorSet['bg'],w=(winWidth-1)/3, c=saveDelayPreset)
cmds.button(label='Rename', bgc=colorSet['bg'],w=(winWidth-1)/3, c=renameDelayPreset)
cmds.button(label='Delete', bgc=colorSet['bg'],w=(winWidth-1)/3, c=deleteDelayPreset)
cmds.setParent('..')

cmds.setParent('..')  # frameLayout Setup Direction

cmds.frameLayout(l='Ovelapping', w=winWidth)

#Button UI
cmds.rowLayout(w=winWidth, numberOfColumns=2, columnWidth2=(200, 100), adjustableColumn=1,
               columnAlign2=['center', 'right'])
mode = cmds.optionMenu(label='Mode : ', w=200, bgc=colorSet['shadow'])
rotMode = cmds.menuItem(label='Rotation')
posMode = cmds.menuItem(label='Position')
previewChk = cmds.checkBox(l='Preview', value=False)
cmds.setParent('..')

gridMode = cmds.gridLayout(cellHeight=30)
cmds.setParent('..')
gridCheck = cmds.gridLayout(cellHeight=7)
cmds.setParent('..')

# Distance / Scene Scale
cmds.rowLayout(h=10, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='')
cmds.text(l='')
cmds.gridLayout(numberOfColumns=5, cellWidthHeight=(30, 10))
cmds.text(l='Near', fn='smallPlainLabelFont')
cmds.text(l='')
cmds.text(l='|')
cmds.text(l='')
cmds.text(l='Far', fn='smallPlainLabelFont')
cmds.setParent('..')
cmds.text(l='      ')
cmds.setParent('..')
cmds.rowLayout(h=20, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='Distance  ', al='right')
distanceT = cmds.floatField(editable=True,value=0,pre=1,max=500)
distanceS = cmds.floatSlider(minValue=0.1, maxValue=500, value=2)
cmds.button(l=' ? ',annotation='Distance from selecion to locator')
cmds.setParent('..')

# Dynamic
cmds.rowLayout(h=10, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='')
cmds.text(l='')
cmds.gridLayout(numberOfColumns=5, cellWidthHeight=(30, 10))
cmds.text(l='Polish', fn='smallPlainLabelFont')
cmds.text(l='')
cmds.text(l='|')
cmds.text(l='')
cmds.text(l='Swing', fn='smallPlainLabelFont')
cmds.setParent('..')
cmds.text(l='      ')
cmds.setParent('..')
cmds.rowLayout(h=20, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='Dynamic  ', al='right')
dynamicT = cmds.intField(editable=True,value=0)
dynamicS = cmds.intSlider(minValue=0, maxValue=5, value=3)
cmds.button(l=' ? ',annotation='Dynamic Simulation')
cmds.setParent('..')

# Offset
cmds.rowLayout(h=10, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='')
cmds.text(l='')
cmds.gridLayout(numberOfColumns=5, cellWidthHeight=(30, 10))
cmds.text(l='Lead', fn='smallPlainLabelFont')
cmds.text(l='')
cmds.text(l='|')
cmds.text(l='')
cmds.text(l='Follow', fn='smallPlainLabelFont')
cmds.setParent('..')
cmds.text(l='      ')
cmds.setParent('..')
cmds.rowLayout(h=20, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='Offset  ', al='right')
offsetT = cmds.floatField(editable=True,value=0,pre=1,min=-10,max=10)
offsetS = cmds.floatSlider(minValue=-5, maxValue=5, value=0)
cmds.button(l=' ? ',annotation='Frame offset to delay animation')
cmds.setParent('..')

cmds.rowLayout(h=20, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='Frame Rate  ', al='right')
fpsF = cmds.intField(editable=False, value=24, bgc=colorSet['bg'])
cmds.text(l='', al='right')
smoothnessChk = cmds.checkBox(l='Smoothness', value=True)
cmds.setParent('..')

overlapB = cmds.button(label='Overlap', bgc=colorSet['yellow'])  # command='DoCheckOverlape'
cmds.setParent('..')

cmds.columnLayout(h=20,bgc=colorSet['shadow']) #Progress
BRSProgressControl = cmds.progressBar(h=20,minValue=0,maxValue=1,progress=0, width=winWidth-5,vis=False)
cmds.setParent('..')  # columnLayout

cmds.frameLayout(l='Keyframe / Breakdown', w=winWidth)

cmds.rowLayout(h=20, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='Breakdown  ', al='right')
breakdownN = cmds.intField(editable=True, value=3)
cmds.text(l='  Frame', al='left')
delLocChk = cmds.checkBox(l='Delete Locator', value=True, al='center')
cmds.setParent('..')

bakeRangeT = cmds.text(l='<range>', fn='obliqueLabelFont')
setKeyB = cmds.button(label='Set Key', bgc=colorSet['yellow'], c=doSetKey)  # command='DoCheckOverlape'
cmds.setParent('..')


# Simulation Check --------------
def overlapeCheck(*_):
    try:
        BRSUpdateUI()
    except:
        pass

    targetList = cmds.ls(selection=True, sn=True)
    configS['isMode'] = cmds.optionMenu(mode, q=True, v=True)
    configS['locDistance'] = float(cmds.floatField(distanceT, q=True, v=True))
    configS['locDynamic'] = int(cmds.intField(dynamicT, q=True, v=True))
    configS['locOffset'] = float(cmds.floatField(offsetT, q=True, v=True))
    configS['smoothness'] = cmds.checkBox(smoothnessChk, q=True, v=True)

    if len(targetList) > 10:
        prompt = cmds.confirmDialog(title='Confirm', message='Selection more than 10 object\nIt may take a long time', button=['Continue', 'Cancel'], defaultButton='Continue',
                           cancelButton='Cancel', dismissString='Cancel')
        if prompt == 'Continue':
            doOverlap(configS['isMode'], configS['locDistance'], configS['locDynamic'], configS['locOffset'], configS['smoothness'])
            cmds.checkBox(previewChk, e=True, v=False)

    elif targetList == []:
        pass
    else:
        doOverlap(configS['isMode'], configS['locDistance'], configS['locDynamic'], configS['locOffset'], configS['smoothness'])
        cmds.checkBox(previewChk, e=True, v=False)
    print ('BRS Delay : Overlaping Finished')
    cmds.inViewMessage(amg='BRS Delay : Overlaping  <hl>Finished</hl>', pos='botCenter', fade=True,
                       fit=250, fst=1000, fot=250)

"""
-----------------------------------------------------------------------
UPDATE
-----------------------------------------------------------------------
"""
def BRSCheckboxUpdate(*_):
    configS['locDistance'] = cmds.checkBox(smoothnessChk, q=True, v=True)
    cmds.checkBox(smoothnessChk, e=True, value=configS['smoothness'])
    BRSUpdateUI()

def BRSFeildUpdate(*_):
    configS['locDistance'] = round(cmds.floatField(distanceT, q=True, v=True),1)
    configS['locDynamic'] = cmds.intField(dynamicT, q=True, v=True)
    configS['locOffset'] = round(cmds.floatField(offsetT, q=True, v=True),1)
    BRSUpdateUI()

def BRSSliderUpdate(*_):
    configS['locDistance'] = round(cmds.floatSlider(distanceS, q=True, value=True),1)
    configS['locDynamic'] = cmds.intSlider(dynamicS, q=True, value=True)
    configS['locOffset'] = round(cmds.floatSlider(offsetS, q=True, value=True),1)
    BRSUpdateUI()

def BRSModeUpdate(*_):
    # delete the old layout and rebuild.
    # the 'or []` below lets you loop even if there are no children....
    for n in cmds.gridLayout(gridMode, q=True, ca=True) or []:
        cmds.deleteUI(n)
    cmds.setParent(gridMode)
    # New Button
    if cmds.optionMenu(mode, q=True, v=True) == 'Rotation':
        cmds.gridLayout(gridMode, e=True, numberOfColumns=4, cellWidth=(winWidth / 4))
        cmds.button('aimXB', label='X', c=setAimX)
        cmds.button('aimYB', label='Y', c=setAimY)
        cmds.button('aimZB', label='Z', c=setAimZ)
        cmds.button('aimIB', label='Invert', c=toggleInvert)
    elif cmds.optionMenu(mode, q=True, v=True) == 'Position':
        cmds.gridLayout(gridMode, e=True, numberOfColumns=3, cellWidth=(winWidth / 3))
        cmds.button('posXZB', label='XZ', c=setPosXZ)
        cmds.button('posYB', label='Y', c=setPosY)
        cmds.button('posXYZB', label='XYZ', c=setPosXYZ)
    # Mode Check
    for n in cmds.gridLayout(gridCheck, q=True, ca=True) or []:
        cmds.deleteUI(n)
    cmds.setParent(gridCheck)
    if cmds.optionMenu(mode, q=True, v=True) == 'Rotation':
        cmds.gridLayout(gridCheck, e=True, numberOfColumns=4, cellWidth=(winWidth / 4), cellHeight=7)
        cmds.text('aimXB_chk', label='', bgc=colorSet['red'])
        cmds.text('aimYB_chk', label='', bgc=colorSet['green'])
        cmds.text('aimZB_chk', label='', bgc=colorSet['blue'])
        cmds.text('aimIB_chk', label='', bgc=colorSet['yellow'])
    elif cmds.optionMenu(mode, q=True, v=True) == 'Position':
        cmds.gridLayout(gridCheck, e=True, numberOfColumns=3, cellWidth=(winWidth / 3), cellHeight=7)
        cmds.text('posXZB_chk', label='', bgc=colorSet['yellow'])
        cmds.text('posYB_chk', label='', bgc=colorSet['yellow'])
        cmds.text('posXYZB_chk', label='', bgc=colorSet['yellow'])
    # Update Highlight Button
    if cmds.optionMenu(mode, q=True, v=True) == 'Rotation':
        if configS['aimX']:
            cmds.text('aimXB_chk', e=True, bgc=colorSet['red'])
            cmds.button('aimXB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimXB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimXB', e=True, bgc=colorSet['highlight'])
        if configS['aimY']:
            cmds.text('aimYB_chk', e=True, bgc=colorSet['green'])
            cmds.button('aimYB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimYB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimYB', e=True, bgc=colorSet['highlight'])
        if configS['aimZ']:
            cmds.text('aimZB_chk', e=True, bgc=colorSet['blue'])
            cmds.button('aimZB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimZB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimZB', e=True, bgc=colorSet['highlight'])
        if configS['aimInvert']:
            cmds.text('aimIB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('aimIB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimIB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimIB', e=True, bgc=colorSet['highlight'])
    elif cmds.optionMenu(mode, q=True, v=True) == 'Position':
        if configS['posXZ']:
            cmds.text('posXZB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('posXZB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('posXZB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('posXZB', e=True, bgc=colorSet['highlight'])
        if configS['posY']:
            cmds.text('posYB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('posYB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('posYB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('posYB', e=True, bgc=colorSet['highlight'])
        if configS['posXYZ']:
            cmds.text('posXYZB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('posXYZB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('posXYZB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('posXYZB', e=True, bgc=colorSet['highlight'])
    configS['isMode'] = cmds.optionMenu(mode, q=True, v=True)


def BRSPresetUIUpdate(*_):
    # Preset UI Update
    global presetMenu
    presetName = cmds.optionMenu(presetMenu, q=True, v=True)
    cmds.deleteUI(presetMenu)
    cmds.setParent(presetCol)
    presetMenu = cmds.optionMenu(label='Preset : ', bgc=colorSet['shadow'], h=20, cc=loadDelayPreset)
    cmds.menuItem(label='Defualt')
    DelayPresetList = os.listdir(presetsDir)
    for i in DelayPresetList:
        pName = (i.split('.')[0])
        if i.__contains__('.json') and not i.__contains__('Defualt'):
            cmds.menuItem(label=pName)
    try:
        cmds.optionMenu(presetMenu, e=True, v=presetName)
    except:
        cmds.optionMenu(presetMenu, e=True, v='Defualt')

def BRSUpdateUI(*_):
    #print (configS)
    clearTemp()
    #Field Update
    cmds.floatField(distanceT, e=True, v=configS['locDistance'])
    cmds.intField(dynamicT, e=True, v=configS['locDynamic'])
    cmds.floatField(offsetT, e=True, v=configS['locOffset'])
    #Slider Update
    cmds.floatSlider(distanceS, e=True, value=configS['locDistance'])
    cmds.intSlider(dynamicS, e=True, value=configS['locDynamic'])
    cmds.floatSlider(offsetS, e=True, value=configS['locOffset'])
    # Set Key Method Check
    #bakeKey = cmds.checkBox(bakeChk, q=True, value=True)
    #breakdown = cmds.checkBox(breakdownChk, q=True, value=True)
    configS['smoothness'] = cmds.checkBox(smoothnessChk, q=True, value=True)

    # Mode
    BRSModeUpdate()

    # Preview
    if cmds.checkBox(previewChk, q=True, v=True) == True:
        clearGuide()
        createGuide(cmds.optionMenu(mode, q=True, v=True), cmds.floatSlider(distanceS, q=True, v=True))
    else:
        clearGuide()

    # Hide Distance on Position Mode
    if cmds.optionMenu(mode, q=True, v=True) == 'Position':
        cmds.floatSlider(distanceS, e=True, minValue=0, v=0)
        cmds.floatField(distanceT, e=True, v=0, editable=False)
    else:
        cmds.floatSlider(distanceS, e=True, minValue=1)
        cmds.floatField(distanceT, e=True, editable=True)

    #Rang Text Update
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    cmds.text(bakeRangeT, e=True, l='frame range [ {} - {} ]'.format(minTime,maxTime))

# Init Update
cmds.button(overlapB, e=True, c=overlapeCheck)
"""
try:
    with open(userFile, 'r') as jsonFile:
        userS = json.load(jsonFile)
        if userS['isTrial'] and userS['days'] > 30:
            cmds.button(overlapB, e=True, c='doOverlap(\'Rotation\', 2.0, 3, 0.0, True);')
except:
    pass
finally:
"""
cmds.checkBox(previewChk, e=True, cc=BRSUpdateUI)
cmds.checkBox(delLocChk, e=True, cc=BRSUpdateUI)
cmds.floatSlider(distanceS, e=True, cc=BRSSliderUpdate, dc=BRSSliderUpdate)
cmds.intSlider(dynamicS, e=True, cc=BRSSliderUpdate, dc=BRSSliderUpdate)
cmds.floatSlider(offsetS, e=True, cc=BRSSliderUpdate, dc=BRSSliderUpdate)
cmds.floatField(distanceT, e=True, ec=BRSFeildUpdate ,cc=BRSFeildUpdate)
cmds.intField(dynamicT, e=True, ec=BRSFeildUpdate,cc=BRSFeildUpdate)
cmds.floatField(offsetT, e=True, ec=BRSFeildUpdate,cc=BRSFeildUpdate)
cmds.optionMenu(mode, e=True, cc=BRSUpdateUI)
BRSUpdateUI()
BRSPresetUIUpdate()

"""
-----------------------------------------------------------------------
START
-----------------------------------------------------------------------
"""
def getFPS(*_):
    timeUnitSet = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
    timeUnit = cmds.currentUnit(q=True, t=True)
    if timeUnit in timeUnitSet:
        return timeUnitSet[timeUnit]
    else:
        return float(str(''.join([i for i in timeUnit if i.isdigit() or i == '.'])))

timeUnitSet = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
timeUnit = cmds.currentUnit(q=True, t=True)
configS['frameRate'] = getFPS()
cmds.intField(fpsF, e=True, v=configS['frameRate'])

def showBRSUI(*_):
    global LocDelay_Version
    try:
        with open(userFile, 'r') as jsonFile:
            userS = json.load(jsonFile)
    except:
        cmds.inViewMessage(amg='<center><h5>Error can\'t install \nplease re-install</h5></center>',
                           pos='botCenter', fade=True,
                           fit=250, fst=2000, fot=250)
        installSource = 'source "' + projectDir.replace('\\', '/') + '/BRS_DragNDrop_Install.mel' + '";'
        mel.eval(installSource)

    else:
        todayDate = dt.datetime.strptime(userS['lastUsedDate'], '%Y-%m-%d')
        regDate = dt.datetime.strptime(userS['registerDate'], '%Y-%m-%d')
        today = str(dt.date.today())
        if today != userS['lastUsedDate']:
            locDeylayService()
            with open(userFile, 'r') as jsonFile:
                userS = json.load(jsonFile)
            with open(userFile, writeMode) as jsonFile:
                userS['lastUsedDate'] = today
                json.dump(userS, jsonFile, indent=4)
        verName = 'LOCATOR DELAY - {}'.format(str(userS['version']))
        cmds.window(winID, e=True, title=verName)
        cmds.showWindow(winID)
        with open(userFile, 'r') as jsonFile:
            userS = json.load(jsonFile)
        with open(userFile, writeMode) as jsonFile:
            userS['used'] = userS['used'] + 1
            userS['version'] = LocDelay_Version
            userS['days'] = abs((regDate - todayDate).days)
            json.dump(userS, jsonFile, indent=4)
    finally:
        pass

"""
-----------------------------------------------------------------------
BURASED UTTHA
-----------------------------------------------------------------------
"""