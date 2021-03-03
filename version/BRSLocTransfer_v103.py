import maya.cmds as cmds

def snap(object, target):
    # snap object to tatget
    snapper = cmds.parentConstraint(target, object, weight=1.0)
    cmds.delete(snapper)

def parentConstraint(object, target):
    # snap object to target
    try:
        cmds.pointConstraint(target, object, weight=1.0, mo=False)
    except:
        pass
    try:
        cmds.orientConstraint(target, object, weight=1.0, mo=False)
    except:
        pass

def BRSSnapAllKeys(object, target, keyList=[]):
    bakeK = cmds.checkBox(BakeChk, q=True, value=True)
    bakeSample = cmds.intField(SampleInt, q=True, v=True)
    cons = cmds.checkBox(ConsChk, q=True, value=True)
    tangentValue = cmds.optionMenu(tangentMode,q=True,v=True)

    tempPosConstr = None
    tempRotConstr = None
    try:
        tempPosConstr = cmds.pointConstraint(target, object, weight=1.0, mo=False)
    except:
        pass
    try:
        tempRotConstr = cmds.orientConstraint(target, object, weight=1.0, mo=False)
    except:
        pass

    if bakeK == True:
        cmds.bakeResults(object, simulation=True, t=(keyList[0], keyList[-1]),
                         sampleBy=bakeSample,
                         oversamplingRate=1, disableImplicitControl=True, preserveOutsideKeys=True,
                         sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False,
                         removeBakedAnimFromLayer=False,
                         bakeOnOverrideLayer=False, minimizeRotation=True, at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))
        cmds.keyTangent(object, itt=tangentValue.lower(), ott=tangentValue.lower(), time=(keyList[0],keyList[-1]) )
    else:
        for frame in keyList:
            cmds.currentTime(frame)
            cmds.setKeyframe(object, itt=tangentValue.lower(), ott=tangentValue.lower(), breakdown=0, hierarchy='none', controlPoints=0,
                             at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

    cmds.delete(tempPosConstr, tempRotConstr)

    if cons == True:
        parentConstraint(target,object)


def objectToLocatorSnap(*_):
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    curTime = cmds.currentTime(query=True)
    anno = cmds.checkBox(AnnoChk, q=True, value=True)
    tangentValue = cmds.optionMenu(tangentMode,q=True,v=True)
    trail = cmds.checkBox(trailChk, q=True, value=True)
    ghost = cmds.checkBox(ghostChk, q=True, value=True)
    bakeK = cmds.checkBox(BakeChk, q=True, value=True)

    selected = cmds.ls(sl=True)
    # print (selected)

    for objName in selected:
        # print(objName)
        keyframeList = []
        attrList = ['translateX',
                    'translateY',
                    'translateZ',
                    'rotateX',
                    'rotateY',
                    'rotateZ'
                    ]

        for keyAttr in attrList:
            keys = cmds.keyframe(objName + '.' + keyAttr, q=True, timeChange=True)
            if keys != None:
                keyframeList = keyframeList + keys
                # print (objName+keyAttr+'  '+str(len(keys)))+ ' Keys'
        if keyframeList == []:
            break
        keyframeList = sorted(list(dict.fromkeys(keyframeList)))
        # print (len(keyframeList))
        # print (keyframeList)

        objNameKeyableAttr = cmds.listAttr(objName, keyable=True)
        # print (objNameKeyableAttr)

        snapLocName = objName + '_BRSSnapLoc'

        # Exist Loc
        try:
            cmds.delete(snapLocName)
        except:
            pass

        # Create Locator
        cmds.spaceLocator(name=snapLocName)
        cmds.setAttr(snapLocName + '.overrideEnabled', 1)
        cmds.setAttr(snapLocName + '.overrideRGBColors', 1)
        cmds.setAttr(snapLocName + '.overrideColorRGB', 0.465, 1, 0.0)
        cmds.setAttr(snapLocName + '.useOutlinerColor', 1)
        cmds.setAttr(snapLocName + '.outlinerColor', 0.7067,1,0)
        snap(snapLocName, objName)

        # Set First Keyframe
        cmds.currentTime(keyframeList[0])
        cmds.setKeyframe(snapLocName, itt=tangentValue.lower(), ott=tangentValue.lower(), breakdown=0, hierarchy='none', controlPoints=0,
                         at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

        # Redraw viewport Off
        cmds.refresh(suspend=True)

        print ('Create ' + snapLocName)
        if len(keyframeList)<=1 and bakeK == True:
            keyframeList = [minTime, maxTime]
        BRSSnapAllKeys(snapLocName, objName, keyframeList)
        cmds.filterCurve(snapLocName + '.translateX',
                         snapLocName + '.translateY',
                         snapLocName + '.translateZ',
                         snapLocName + '.rotateX',
                         snapLocName + '.rotateY',
                         snapLocName + '.rotateZ')

        # Annotate
        annoText = objName
        if annoText.__contains__(':') :
            annoText = (annoText.split(':')).pop()
        annotateShape = cmds.annotate(snapLocName, tx=annoText)
        cmds.pickWalk(d='up')
        annotate = (cmds.ls(sl=True))[0]
        cmds.parent(annotate, snapLocName)
        cmds.setAttr(annotate + '.overrideEnabled', 1)
        cmds.setAttr(annotate + '.overrideDisplayType', 2)
        cmds.setAttr(annotateShape + '.displayArrow', 0)
        cmds.setAttr(annotate + '.translateX', 0)
        cmds.setAttr(annotate + '.translateY', 0)
        cmds.setAttr(annotate + '.translateZ', 0)
        cmds.setAttr(annotate + '.hiddenInOutliner', True)
        cmds.rename(annotate, objName + '_annotate')
        if anno == False:
            cmds.delete(objName + '_annotate')
        if trail :
            BRSArc(objName,snapLocName,[minTime,maxTime])
        if ghost :
            BRSGhost(snapLocName)

    # Finish
    cmds.currentTime(curTime)
    cmds.select(selected, r=True)

    # Redraw viewport On
    cmds.refresh(suspend=False)


def locatorToObjectSnap(*_):
    cmds.delete(cmds.ls(dag=1, ap=1, sl=1, type="constraint"))
    minTime = cmds.playbackOptions(q=True, minTime=True)
    maxTime = cmds.playbackOptions(q=True, maxTime=True)
    curTime = cmds.currentTime(query=True)
    bakeK = cmds.checkBox(BakeChk, q=True, value=True)
    tangentValue = cmds.optionMenu(tangentMode,q=True,v=True)

    # Redraw viewport Off
    cmds.refresh(suspend=True)

    selected = cmds.ls(sl=True)

    for objName in selected:
        snapLocName = objName + '_BRSSnapLoc'
        try:
            cmds.select(snapLocName)
        except:
            pass
        else:
            # Delete Keys
            try:
                cmds.cutKey(objName, cl=True, at=('tx', 'ty', 'tz'))
            except:
                pass
            try:
                cmds.cutKey(objName, cl=True, at=('rx', 'ry', 'rz'))
            except:
                pass

            keyframeList = []
            attrList = ['translateX',
                        'translateY',
                        'translateZ',
                        'rotateX',
                        'rotateY',
                        'rotateZ'
                        ]

            for keyAttr in attrList:
                keys = cmds.keyframe(snapLocName + '.' + keyAttr, q=True, timeChange=True)
                if keys != None:
                    keyframeList = keyframeList + keys
                    # print (objName+keyAttr+'  '+str(len(keys)))+ ' Keys'
            if keyframeList == []:
                break

            keyframeList = sorted(list(dict.fromkeys(keyframeList)))
            # print (len(keyframeList))
            # print (keyframeList)

            # Set First Keyframe
            cmds.currentTime(keyframeList[0])
            cmds.setKeyframe(objName, itt=tangentValue.lower(), ott=tangentValue.lower(), breakdown=0, hierarchy='none', controlPoints=0,
                             at=('tx', 'ty', 'tz', 'rx', 'ry', 'rz'))

            if len(keyframeList)<=1 and bakeK == True:
                keyframeList = [minTime,maxTime]
            BRSSnapAllKeys(objName, snapLocName, keyframeList)
            print ('Delete ' + snapLocName)
            cmds.delete(snapLocName)
    # Finish
    cmds.currentTime(curTime)
    cmds.select(selected, r=True)
    cmds.checkBox(BakeChk, e=True, value=False)

    # Redraw viewport On
    cmds.refresh(suspend=False)

def BRSArc(name,target,keyList=[cmds.playbackOptions(q=True, minTime=True),cmds.playbackOptions(q=True, maxTime=True)]):
    cmds.snapshot(n=name+'_Arc', motionTrail=True, increment=True, startTime=keyList[0],endTime=keyList[-1])
    cmds.setAttr (name+'_Arc'+'HandleShape.trailColor',0.7067,1,0,type='double3')
    cmds.setAttr (name+'_Arc'+'HandleShape.extraTrailColor',0.0601,0.0601,0.0601,type='double3')
    cmds.setAttr (name+'_Arc'+'HandleShape.trailDrawMode',1)

def BRSGhost(target):
    cmds.setAttr (target+'Shape.ghosting',1)
    cmds.setAttr (target+'Shape.ghostingControl',0)
    cmds.setAttr (target+'Shape.ghostColorPreA',0.4)
    cmds.setAttr (target+'Shape.ghostColorPostA',0.4)
    cmds.setAttr (target+'Shape.ghostColorPre',1,1,0,type='double3')
    cmds.setAttr (target+'Shape.ghostColorPost',1,0,0,type='double3')

def uiUpdate(*_):
    bakeK = cmds.checkBox(BakeChk, q=True, value=True)
    if bakeK == True:
        cmds.intField(SampleInt, e=True, editable=True, vis=True,bgc=(0,0,0))
    else:
        cmds.intField(SampleInt, e=True, editable=False, vis=True,bgc=colorSet['bg'])


"""
-----------------------------------------------------------------------
UI
-----------------------------------------------------------------------
"""
version = '1.03'
winID = 'BRSLOCTRANSFER'
winWidth = 200

colorSet = {
    'bg': (.2, .2, .2),
    'red': (0.8, 0.4, 0),
    'green': (0.7067,1,0),
    'blue': (0, 0.4, 0.8),
    'yellow': (1, 0.8, 0),
    'shadow': (.15, .15, .15),
    'highlight': (.3, .3, .3)
}

if cmds.window(winID, exists=True):
    cmds.deleteUI(winID)
cmds.window(winID, t='BRS Locator Transfer' + ' - ' + version,
            w=winWidth, sizeable=True,
            retain=True, bgc=colorSet['bg'])

cmds.columnLayout(adj=True, w=winWidth)
cmds.text(l='BRS Locator Transfer' + ' - ' + version, fn='boldLabelFont', h=20, bgc=colorSet['green'])
cmds.rowLayout(numberOfColumns=1, columnWidth1=winWidth-1)
tangentMode = cmds.optionMenu(label='Key Tangent : ', w=200, bgc=colorSet['shadow'])
cmds.menuItem(label='Auto')
cmds.menuItem(label='Step')
cmds.setParent('..')
cmds.rowLayout(numberOfColumns=2, columnWidth2=(winWidth * 0.5, winWidth * 0.5), columnAlign2=['center', 'center'])
ConsChk = cmds.checkBox(label='Constraint', align='center',v=True)
AnnoChk = cmds.checkBox(label='Annotation', align='center',v=True)
cmds.setParent('..')
cmds.rowLayout(numberOfColumns=2, columnWidth2=(winWidth * 0.5, winWidth * 0.5), columnAlign2=['center', 'center'])
trailChk = cmds.checkBox(label='Motion Trail', align='center',v=False)
ghostChk = cmds.checkBox(label='Ghosting', align='center',v=False)
cmds.setParent('..')
cmds.rowLayout(numberOfColumns=2, columnWidth2=(winWidth * 0.5, winWidth * 0.5), columnAlign2=['center', 'center'])
BakeChk = cmds.checkBox(label='Bake Keyframe', align='center', cc=uiUpdate)
SampleInt = cmds.intField(editable=False, min=1, max=5, v=1, step=1, vis=True ,bgc=colorSet['bg'])
cmds.setParent('..')
cmds.rowLayout(numberOfColumns=1, columnWidth1=winWidth-1)
cmds.button(l='Store Locator', h=25 ,w=winWidth-1 , c=objectToLocatorSnap, bgc=colorSet['highlight'])
cmds.setParent('..')
cmds.rowLayout(numberOfColumns=1, columnWidth1=winWidth-1)
cmds.button(l='Transfer Back', h=25 ,w=winWidth-1 , c=locatorToObjectSnap, bgc=colorSet['highlight'])
cmds.setParent('..')
cmds.text(l='Created by Burasate Uttha', h=20, al='left', fn='smallPlainLabelFont')
cmds.showWindow(winID)
# Redraw viewport On
cmds.refresh(suspend=False)
