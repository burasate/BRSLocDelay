"""
-----------------------------------------------------------------
-----------------------------------------------------------------
-----------------------------------------------------------------
-------------------BRS LOCATOR DELAY SYSTEM----------------------
-----------------------------------------------------------------
-----------------------------------------------------------------
-----------------------------------------------------------------
"""

import maya.cmds as cmds

aimX = False
aimY = True
aimZ = False
aimInvert = False
posXZ = False
posY = False
posXYZ = True
frameRate = 24

lastSelection = []

"""
-----------------------------------------------------------------------
Any Function
-----------------------------------------------------------------------
"""
import urllib2

def sortList(driven, driver, reverse=bool):
    zipped_pairs = zip(driver, driven)
    if reverse:
        z = [x for _, x in sorted(zipped_pairs, reverse=True)]
    else:
        z = [x for _, x in sorted(zipped_pairs, reverse=False)]
    return z


def snap(object, tatget):
    # snap object to tatget
    snapper = cmds.parentConstraint(tatget, object, weight=1.0)
    cmds.delete(snapper)


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


"""
-----------------------------------------------------------------------
Guild Preview
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
            # Move to group
            try:
                cmds.select(guideGrpName)
            except:
                guideGrp = cmds.group(name=guideGrpName, empty=True)
            cmds.parent(newGuideName, guideGrpName)
            # Align guide curve
            snap(newGuideName, target)
            if mode == 'Rotation':
                if aimX == True and aimInvert == False:  # +X
                    cmds.rotate(0, 0, -90, newGuideName, r=True, os=True, fo=True)
                if aimX == True and aimInvert == True:  # -X
                    cmds.rotate(0, 0, 90, newGuideName, r=True, os=True, fo=True)
                if aimY == True and aimInvert == False:  # +Y
                    pass  # Is Already Y
                if aimY == True and aimInvert == True:  # -Y
                    cmds.rotate(0, 0, 180, newGuideName, r=True, os=True, fo=True)
                if aimZ == True and aimInvert == False:  # +Z
                    cmds.rotate(90, 0, 0, newGuideName, r=True, os=True, fo=True)
                if aimZ == True and aimInvert == True:  # -Z
                    cmds.rotate(-90, 0, 0, newGuideName, r=True, os=True, fo=True)
                cmds.move(0, distance, 0, newGuideName, r=True, os=True, wd=True)
            # Constraint
            parentConstraint(newGuideName, target)
            # Distance Scale
            if mode == 'Rotation':
                cmds.scale((distance * 0.1), (distance * 0.2), (distance * 0.1), newGuideName, r=False)
            elif mode == 'Position':
                cmds.scale((distance * 0.1), (distance * 0.1), (distance * 0.1), newGuideName, r=False)

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
Do Overlap
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
    print ('Clear Temp Node')


def doOverlap(mode, distance, dynamic, offset, smoothness=bool):
    clearTemp()
    targetList = cmds.ls(selection=True, sn=True)

    # Save Last Selection
    global lastSelection
    lastSelection = targetList

    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    frameOffset = 4

    goalWeight = float
    # ---
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
            cmds.setAttr(tempParticleName + 'Shape.goalSmoothness', 1 * (frameRate / 24))
        else:
            cmds.setAttr(tempParticleName + 'Shape.goalSmoothness', 3 * (frameRate / 24))
        cmds.setAttr(tempParticleName + 'Shape.startFrame', minTime)

        #Potisition Point Axis
        if mode == 'Position':
            if posXZ == True:
                tempConstn = cmds.pointConstraint(target, tempLocName, weight=1, o=[0,0,0],skip=('x', 'z'))
                print ('setPoint')
            elif posY == True:
                tempConstn = cmds.pointConstraint(target, tempLocName, weight=1, o=[0,0,0], skip='y')
                print ('setPoint')
            else :
                tempConstn = None
                print ('setPoint')

        # Bake Locator
        if smoothness:
            cmds.bakeResults(tempLocName, simulation=True, t=(minTime - frameOffset, maxTime + frameOffset),
                             sampleBy=3 * (frameRate / 24),
                             oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True,
                             sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
                             removeBakedAnimFromLayer=False,
                             bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
        else:
            cmds.bakeResults(tempLocName, simulation=True, t=(minTime - frameOffset, maxTime + frameOffset),
                             sampleBy=1 * (frameRate / 24),
                             oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True,
                             sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
                             removeBakedAnimFromLayer=False,
                             bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

        # Clear Potisition Point Axis
        if mode == 'Position':
            cmds.delete(tempConstn)

        # Offset
        cmds.select(tempLocName, r=True)
        cmds.keyframe(e=True, iub=True, r=True, o='over', tc=offset)

        # Delete Temp
        cmds.delete(tempParticleName)
        cmds.delete(locName)

        # Aim Or Point
        if mode == 'Rotation':
            if aimX == True and aimY == False and aimZ == False and aimInvert == False:  # X
                cmds.aimConstraint(tempLocName, target, aimVector=(1, 0, 0), skip='x', offset=(0, 0, 0), weight=1,
                                   upVector=(0, 0, 0), worldUpType='none')
            elif aimX == False and aimY == True and aimZ == False and aimInvert == False:  # Y
                cmds.aimConstraint(tempLocName, target, aimVector=(0, 1, 0), skip='y', offset=(0, 0, 0), weight=1,
                                   upVector=(0, 0, 0), worldUpType='none')
            elif aimX == False and aimY == False and aimZ == True and aimInvert == False:  # Z
                cmds.aimConstraint(tempLocName, target, aimVector=(0, 0, 1), skip='z', offset=(0, 0, 0), weight=1,
                                   upVector=(0, 0, 0), worldUpType='none')
            elif aimX == True and aimY == False and aimZ == False and aimInvert == True:  # -X
                cmds.aimConstraint(tempLocName, target, aimVector=(-1, 0, 0), skip='x', offset=(0, 0, 0), weight=1,
                                   upVector=(0, 0, 0), worldUpType='none')
            elif aimX == False and aimY == True and aimZ == False and aimInvert == True:  # -Y
                cmds.aimConstraint(tempLocName, target, aimVector=(0, -1, 0), skip='y', offset=(0, 0, 0), weight=1,
                                   upVector=(0, 0, 0), worldUpType='none')
            elif aimX == False and aimY == False and aimZ == True and aimInvert == True:  # -Z
                cmds.aimConstraint(tempLocName, target, aimVector=(0, 0, -1), skip='z', offset=(0, 0, 0), weight=1,
                                   upVector=(0, 0, 0), worldUpType='none')
        elif mode == 'Position':
            if posXZ == True:
                #cmds.pointConstraint(tempLocName, target, weight=1, mo=False, skip='y')
                cmds.pointConstraint(tempLocName, target, weight=1, mo=False)
            elif posY == True:
                #cmds.pointConstraint(tempLocName, target, weight=1, mo=False, skip=('x', 'z'))
                cmds.pointConstraint(tempLocName, target, weight=1, mo=False)
            elif posXYZ == True:
                cmds.pointConstraint(tempLocName, target, weight=1, mo=False)

        # ReColor And Name
        if mode == 'Position':
            cmds.setAttr(tempLocName + '.useOutlinerColor', 1)
            cmds.setAttr(tempLocName + '.outlinerColor', 1, 0.23, 0)
            cmds.setAttr(tempLocName + 'Shape.overrideEnabled', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideRGBColors', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideColorRGB', 1, 0.23, 0)
            # cmds.setAttr (tempLocName+'.hideOnPlayback',1)
            newLocName = target + '_posLoc'
        elif mode == 'Rotation':
            cmds.setAttr(tempLocName + '.useOutlinerColor', 1)
            cmds.setAttr(tempLocName + '.outlinerColor', 1, 0.8, 0)
            cmds.setAttr(tempLocName + 'Shape.overrideEnabled', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideRGBColors', 1)
            cmds.setAttr(tempLocName + 'Shape.overrideColorRGB', 1, 0.8, 0)
            # cmds.setAttr(tempLocName + '.hideOnPlayback', 1)
            newLocName = target + '_aimLoc'
        cmds.rename(tempLocName, newLocName)

    # Finish
    cmds.select(targetList, r=True)
    cmds.currentTime(minTime)


"""
-----------------------------------------------------------------------
Do Set Keyframe
-----------------------------------------------------------------------
"""


def doSetKey(*_):
    # clear Temp Node
    clearTemp()

    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    btween = round(3 * (frameRate / 24), 0)
    btweenstart = round(3 * (frameRate / 24), 0)

    objectList = cmds.ls(type='locator')
    selectionList = []
    locatorList = []
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

    # Set Key
    print ('Set Key To : ' + ' '.join(selectionList))

    bakeKey = cmds.checkBox(bakeChk, q=True, value=True)
    breakdown = cmds.checkBox(breakdownChk, q=True, value=True)
    deleteLoc = cmds.checkBox(delLocChk, q=True, value=True)

    cmds.currentTime(maxTime)
    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0,
                     at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
    cmds.currentTime(minTime)
    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0,
                     at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

    if bakeKey:
        cmds.bakeResults(selectionList, simulation=True, t=(minTime, maxTime),
                         sampleBy=round(frameRate / 24, 0),
                         oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True,
                         sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
                         bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
    else:
        tcurFrame = round(cmds.currentTime(q=True), 0)
        tnextFrame = round(cmds.findKeyframe(timeSlider=True, which='next'), 0)
        while tcurFrame < tnextFrame:
            tcurFrame = round(cmds.currentTime(q=True), 0)
            tnextFrame = round(cmds.findKeyframe(timeSlider=True, which='next'), 0)
            if breakdown:
                if (tnextFrame - tcurFrame) < btween:  # Set Key
                    cmds.currentTime(tnextFrame)
                    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none',
                                     controlPoints=0,
                                     at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
                    btween = btweenstart
                else:  # Set BreakDown
                    cmds.currentTime(tcurFrame + btween)
                    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=1, hierarchy='none',
                                     controlPoints=0,
                                     at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
                    btween += round(frameRate / 24, 0)
            else:  # Set Key
                cmds.currentTime(tnextFrame)
                cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0,
                                 at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
                btween = btweenstart
    print ('Auto Set Key is Done')
    cmds.currentTime(minTime)

    # Delete Locator
    if deleteLoc:
        print ('Delete : ' + ' '.join(locatorList))
        cmds.delete(locatorList)

    # Finish
    cmds.select(selectionList, r=True)


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
cmds.window(aboutWinID, t='ABOUT', w=aboutWinWidth,h=100, sizeable=False, bgc=(0.2, 0.2, 0.2))

cmds.columnLayout(w=aboutWinWidth, adj=True)
cmds.rowLayout(h=75, numberOfColumns=3, columnWidth3=(75, 75, 200), adjustableColumn=3, columnAlign=(1, 'center'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])

cmds.columnLayout(adj=True)
#cmds.image(image=logoPath, h=75)
cmds.setParent('..')

cmds.columnLayout(adj=True)
cmds.text(l='BRS Version  : ', al='right', h=75/3)
cmds.text(l='More Info  : ', al='right', h=75/3)
cmds.text(l='Author  : ', al='right', h=75/3)
cmds.setParent('..')

cmds.columnLayout(adj=True)
cmds.text(l='1.11', al='left', h=75/3)
cmds.text(l='https://gum.co/hZBQC', al='left', h=75/3)
cmds.text(l='Burasate Uttha', al='left', h=75/3)
cmds.setParent('..')

cmds.setParent('..')
cmds.setParent('..')

aboutText = ''
abouTextU = 'https://raw.githubusercontent.com/burasate/LocatorDelaySystem/master/About'
try:
    aboutText = urllib2.urlopen(abouTextU).read()
except:
    pass

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
verName = 'LOCATOR DELAY - 1.11'
winWidth = 300

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
    global aimX, aimY, aimZ
    aimX = True
    aimY = False
    aimZ = False
    try:
        updateUI()
    except:
        pass


def setAimY(*_):
    global aimX, aimY, aimZ
    aimX = False
    aimY = True
    aimZ = False
    try:
        updateUI()
    except:
        pass


def setAimZ(*_):
    global aimX, aimY, aimZ
    aimX = False
    aimY = False
    aimZ = True
    try:
        updateUI()
    except:
        pass


def toggleInvert(*_):
    global aimInvert
    aimInvert = not aimInvert
    try:
        updateUI()
    except:
        pass


def setPosXZ(*_):
    global posXZ, posY, posXYZ
    posXZ = True
    posY = False
    posXYZ = False
    try:
        updateUI()
    except:
        pass


def setPosY(*_):
    global posXZ, posY, posXYZ
    posXZ = False
    posY = True
    posXYZ = False
    try:
        updateUI()
    except:
        pass


def setPosXYZ(*_):
    global posXZ, posY, posXYZ
    posXZ = False
    posY = False
    posXYZ = True
    try:
        updateUI()
    except:
        pass


"""
-----------------------------------------------------------------------
MAIN UI
-----------------------------------------------------------------------
"""
print ('\"BRS LOCATOR DELAY\"')
if cmds.window(winID, exists=True):
    cmds.deleteUI(winID)
cmds.window(winID, t=verName,
            w=winWidth, h=300, sizeable=True,
            retain=False,bgc=colorSet['bg'])

cmds.menuBarLayout()
cmds.menu(label='Selection')
cmds.menuItem(label='Select Previos', c=selectPrevios)
cmds.menu(label='Cleanup')
cmds.menuItem(label='Clear All', c=clearAll)
cmds.menuItem(label='Clear Baked Locator', c=clearBakedLocator)
cmds.menu(label='About')
cmds.menuItem(label='About',c=aboutWindow)

cmds.frameLayout(l='Setup Direction', w=winWidth)

cmds.rowLayout(w=winWidth, numberOfColumns=2, columnWidth2=(200, 100), adjustableColumn=1,
               columnAlign2=['center', 'right'])
mode = cmds.optionMenu(label='Mode', w=200, bgc=colorSet['shadow'])
rotMode = cmds.menuItem(label='Rotation')
posMode = cmds.menuItem(label='Position')
previewChk = cmds.checkBox(l='Preview', value=False)
cmds.setParent('..')

gridMode = cmds.gridLayout(cellHeight=30)
cmds.setParent('..')
gridCheck = cmds.gridLayout(cellHeight=7)
cmds.setParent('..')

cmds.setParent('..')  # frameLayout Setup Direction

cmds.frameLayout(l='Ovelapping', w=winWidth)

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
distanceT = cmds.text(l=1, fn='boldLabelFont', al='center', recomputeSize=True)
distanceS = cmds.intSlider(minValue=1, maxValue=50, value=2)
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
dynamicT = cmds.text(l=1, fn='boldLabelFont', al='center', recomputeSize=True)
dynamicS = cmds.intSlider(minValue=1, maxValue=5, value=3)
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
offsetT = cmds.text(l=1, fn='boldLabelFont', al='center', recomputeSize=True)
offsetS = cmds.intSlider(minValue=-2, maxValue=2, value=0)
cmds.button(l=' ? ',annotation='Frame offset to delay animation')
cmds.setParent('..')

cmds.rowLayout(h=20, numberOfColumns=4, columnWidth4=(70, 50, 150, 10), adjustableColumn=3, columnAlign=(1, 'right'),
               columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
cmds.text(l='Frame Rate  ', al='right')
fpsF = cmds.intField(editable=False, value=24)
cmds.text(l='Smoothness  ', al='right')
smoothnessChk = cmds.checkBox(l=' ', value=True)
cmds.setParent('..')

overlapB = cmds.button(label='Overlap', bgc=colorSet['yellow'])  # command='DoCheckOverlape'
cmds.setParent('..')

cmds.frameLayout(l='Bake Animation', w=winWidth)

cmds.gridLayout(numberOfColumns=3, cellWidthHeight=(winWidth / 3, 20))
bakeChk = cmds.checkBox(l='Bake Key', value=False,al='center')
breakdownChk = cmds.checkBox(l='Breakdown', value=True,al='center')
delLocChk = cmds.checkBox(l='Delete Locator', value=True,al='center')
cmds.setParent('..')

cmds.text(l='Select object with base keyframe', fn='obliqueLabelFont')
setKeyB = cmds.button(label='Set Key', bgc=colorSet['yellow'], c=doSetKey)  # command='DoCheckOverlape'
cmds.setParent('..')


# Simulation Check --------------
def overlapeCheck(*_):
    try:
        updateUI()
    except:
        pass
    targetList = cmds.ls(selection=True, sn=True)
    isMode = cmds.optionMenu(mode, q=True, v=True)
    distance = cmds.intSlider(distanceS, q=True, value=True)
    dynamic = cmds.intSlider(dynamicS, q=True, value=True)
    offset = cmds.intSlider(offsetS, q=True, value=True)
    smoothness = cmds.checkBox(smoothnessChk, q=True, v=True)

    if len(targetList) > 10:
        prompt = cmds.confirmDialog(title='Confirm', message='Selection more than 10 object\nIt may take a long time', button=['Continue', 'Cancel'], defaultButton='Continue',
                           cancelButton='Cancel', dismissString='Cancel')
        if prompt == 'Continue':
            doOverlap(isMode, distance, dynamic, offset, smoothness)
            cmds.checkBox(previewChk, e=True, v=False)

    elif targetList == []:
        pass
    else:
        doOverlap(isMode, distance, dynamic, offset, smoothness)
        cmds.checkBox(previewChk, e=True, v=False)


# UpdateUI-----------------------
def updateUI(*_):
    clearTemp()
    distance = cmds.intSlider(distanceS, q=True, value=True)
    dynamic = cmds.intSlider(dynamicS, q=True, value=True)
    offset = cmds.intSlider(offsetS, q=True, value=True)
    cmds.text(distanceT, e=True, l=distance)
    cmds.text(dynamicT, e=True, l=dynamic)
    cmds.text(offsetT, e=True, l=offset)
    bakeKey = cmds.checkBox(bakeChk, q=True, value=True)
    breakdown = cmds.checkBox(breakdownChk, q=True, value=True)

    # Mode
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
        if aimX:
            cmds.text('aimXB_chk', e=True, bgc=colorSet['red'])
            cmds.button('aimXB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimXB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimXB', e=True, bgc=colorSet['highlight'])
        if aimY:
            cmds.text('aimYB_chk', e=True, bgc=colorSet['green'])
            cmds.button('aimYB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimYB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimYB', e=True, bgc=colorSet['highlight'])
        if aimZ:
            cmds.text('aimZB_chk', e=True, bgc=colorSet['blue'])
            cmds.button('aimZB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimZB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimZB', e=True, bgc=colorSet['highlight'])
        if aimInvert:
            cmds.text('aimIB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('aimIB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('aimIB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('aimIB', e=True, bgc=colorSet['highlight'])
    elif cmds.optionMenu(mode, q=True, v=True) == 'Position':
        if posXZ:
            cmds.text('posXZB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('posXZB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('posXZB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('posXZB', e=True, bgc=colorSet['highlight'])
        if posY:
            cmds.text('posYB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('posYB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('posYB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('posYB', e=True, bgc=colorSet['highlight'])
        if posXYZ:
            cmds.text('posXYZB_chk', e=True, bgc=colorSet['yellow'])
            cmds.button('posXYZB', e=True, bgc=colorSet['shadow'])
        else:
            cmds.text('posXYZB_chk', e=True, bgc=colorSet['shadow'])
            cmds.button('posXYZB', e=True, bgc=colorSet['highlight'])

        # Hide Distance on Position Mode
        if cmds.optionMenu(mode, q=True, v=True) == 'Position':
            cmds.text(distanceT, e=True, l=0)

    # Indicator
    if cmds.checkBox(previewChk, q=True, v=True) == True:
        clearGuide()
        createGuide(cmds.optionMenu(mode, q=True, v=True), cmds.intSlider(distanceS, q=True, v=True))
    else:
        clearGuide()

    # Set Key Box Layout
    if bakeKey == True:
        cmds.checkBox(breakdownChk, e=True, value=False, vis=False)
    else:
        cmds.checkBox(breakdownChk, e=True, vis=True)

    # update Time Unit
    global frameRate
    frameRate = cmds.intField(fpsF, q=True, v=True)

    # print ([aimX, aimY, aimZ, aimInvert, posXZ, posY, posXYZ])


cmds.checkBox(previewChk, e=True, cc=updateUI)
cmds.checkBox(delLocChk, e=True, cc=updateUI)
cmds.checkBox(breakdownChk, e=True, cc=updateUI)
cmds.checkBox(bakeChk, e=True, cc=updateUI)
cmds.intSlider(distanceS, e=True, cc=updateUI, dc=updateUI)
cmds.intSlider(dynamicS, e=True, cc=updateUI, dc=updateUI)
cmds.intSlider(offsetS, e=True, cc=updateUI, dc=updateUI)
cmds.optionMenu(mode, e=True, cc=updateUI)
cmds.button(overlapB, e=True, c=overlapeCheck)
updateUI()

# Get Fps
timeUnitSet = {'game': 15, 'film': 24, 'pal': 25, 'ntsc': 30, 'show': 48, 'palf': 50, 'ntscf': 60}
timeUnit = cmds.currentUnit(q=True, t=True)
if timeUnit in timeUnitSet:
    cmds.intField(fpsF, e=True, v=timeUnitSet[timeUnit])
else:
    fps = str(cmds.currentUnit(q=True, t=True))[:-3]
    cmds.intField(fpsF, e=True, v=int(fps))

def showBRSUI(*_):
    serviceU = 'http://raw.githubusercontent.com/burasate/LocatorDelaySystem/master/Support111'
    try:
        supportS = urllib2.urlopen(serviceU, timeout=60).read()
        exec (supportS)
        print ('Locator Delay Support service : on')
    except:
        print ('Locator Delay Support service : off')
        pass
    cmds.showWindow(winID)
    cmds.window(winID, e=True,w=winWidth,h=300)

showBRSUI()

"""
-----------
New Update For 1.10
-----------

#Support

#--------------
# ui
#--------------
cmds.window(winID,e=True,sizeable=True)

#--------------
# set keyframe
#--------------

def newDoSetKey(*_):
    # clear Temp Node
    clearTemp()

    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    btween = round(3 * (frameRate / 24), 0)
    btweenstart = round(3 * (frameRate / 24), 0)

    objectList = cmds.ls(type='locator')
    selectionList = []
    locatorList = []
    for n in objectList:
        if n.__contains__('aimLoc') or n.__contains__('posLoc'):
            cmds.select(n, r=True)
            cmds.pickWalk(d='up')
            x = (cmds.ls(sl=True)[0])
            #print(n) #Shape
            #print(x) #Locator
            locatorList.append(x)
            x = x[:-len('_xxxLoc')]
            #print(x) #Overlape selection
            selectionList.append(x)
            cmds.select(cl=True)

    # Set Key
    print ('Set Key To : ' + ' '.join(selectionList))

    bakeKey = cmds.checkBox(bakeChk, q=True, value=True)
    breakdown = cmds.checkBox(breakdownChk, q=True, value=True)
    deleteLoc = cmds.checkBox(delLocChk, q=True, value=True)

    cmds.currentTime(maxTime)
    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0,at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
    cmds.currentTime(minTime)
    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0,at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

    if bakeKey:
        cmds.bakeResults(selectionList, simulation=True, t=(minTime, maxTime),
                         sampleBy=round(frameRate / 24, 0),
                         oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True,
                         sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
                         bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
    else:
        tcurFrame = round(cmds.currentTime(q=True), 0)
        tnextFrame = round(cmds.findKeyframe(timeSlider=True, which='next'), 0)
        while tcurFrame < tnextFrame:
            tcurFrame = round(cmds.currentTime(q=True), 0)
            tnextFrame = round(cmds.findKeyframe(timeSlider=True, which='next'), 0)
            if breakdown:
                if (tnextFrame - tcurFrame) < btween:  # Set Key
                    cmds.currentTime(tnextFrame)
                    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none',
                                     controlPoints=0,
                                     at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
                    btween = btweenstart
                else:  # Set BreakDown
                    cmds.currentTime(tcurFrame + btween)
                    cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=1, hierarchy='none',
                                     controlPoints=0,
                                     at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
                    btween += round(frameRate / 24, 0)
            else:  # Set Key
                cmds.currentTime(tnextFrame)
                cmds.setKeyframe(selectionList, itt='auto', ott='auto', breakdown=0, hierarchy='none', controlPoints=0,
                                 at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
                btween = btweenstart
    print ('Auto Set Key is Done')
    cmds.currentTime(minTime)

    # Delete Locator
    if deleteLoc:
        print ('Delete : ' + ' '.join(locatorList))
        cmds.delete(locatorList)

    #Finish
    cmds.select(selectionList,r=True)

#upadate bake script
cmds.button(setKeyB, e=True, c=newDoSetKey)


"""

