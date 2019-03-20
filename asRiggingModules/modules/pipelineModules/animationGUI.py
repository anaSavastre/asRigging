import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaAnim as omAnim
import sys
import socket
import os 
from os import listdir
from functools import partial
from os.path import split, isfile, join, dirname

# import pipeline as pl
import functions as fn
import mayaModule as mmod
import controlFn as ctlFn
import rigFn as rigFn
import math


def linePointDistance (line, point):
    return abs((line[0]*point[0] +line[1]*point[1]+line[2]))/math.sqrt(line[0]*line[0]+line[1]*line[1])

def lineEquation(point1, point2):
    '''
    Returns coefficients a, b, c of equation:
    ax +by +c =0 
    '''
    b = point2[0] - point1[0]
    a = point1[1] - point2[1]
    c = point1[0]*point2[1] - point2[0]*point1[1]

    return a, b, c


def getLocalOffset(parent, child):
    parentWorldMatrix = fn.getDagPath(parent).inclusiveMatrix()
    childWorldMatrix = fn.getDagPath(child).inclusiveMatrix()

    offsetMatrix = childWorldMatrix * parentWorldMatrix.inverse()
    scriptUtils = om.MScriptUtil()
    returnMatrix = om.MTransformationMatrix()
    translationVector = om.MVector()
    scaleDouble = scriptUtils.asDouble3Ptr()
    rotationMatrix = om.MTransformationMatrix(offsetMatrix)
    rotationMatrix.setTranslation(translationVector, om.MSpace.kWorld)
    # rotationMatrix.setScale(scaleDouble, om.MSpace.kWorld)


    transformMatrix = om.MTransformationMatrix(offsetMatrix)
    translationVector = transformMatrix.getTranslation(om.MSpace.kWorld)


    # returnMatrix = offsetMatrix    
    returnMatrix.setTranslation(translationVector, om.MSpace.kWorld)


    return returnMatrix.asMatrix()

    
class animationGUI (object):

    def __init__(self, dockUI=True):

        # GLOBALS
        self.windowName = "asAnimationGUI"
        self.workSpace = "asAnimationWorkSpace"
        self.dockControl = "asAnimationGUIDock"
        self.dock = dockUI
        self.windowWidth = 330
        self.windowHeight = 180
        self.animationGui()
        self.animationCurve = None
        self.timeArray=None
        self.valueArray=None

    
    def getLocalOffset(self, parent, child, translationOffsetFlag = True, rotationOffsetFlag = True):
        parentWorldMatrix = fn.getDagPath(parent).inclusiveMatrix()
        childWorldMatrix = fn.getDagPath(child).inclusiveMatrix()

        offsetMatrix = childWorldMatrix * parentWorldMatrix.inverse()
        scriptUtils = om.MScriptUtil()
        returnMatrix = om.MTransformationMatrix()
        translationVector = om.MVector()
        scaleDouble = scriptUtils.asDouble3Ptr()
        # rotationMatrix.setScale(scaleDouble, om.MSpace.kWorld)


        transformMatrix = om.MTransformationMatrix(offsetMatrix)
        if (translationOffsetFlag):
            translationVector = transformMatrix.getTranslation(om.MSpace.kWorld)
        if (rotationOffsetFlag):
            rotationMatrix = om.MTransformationMatrix(offsetMatrix)
            rotationMatrix.setTranslation(translationVector, om.MSpace.kWorld)
            returnMatrix = rotationMatrix  
            
        # returnMatrix = offsetMatrix  
        returnMatrix.setTranslation(translationVector, om.MSpace.kWorld)

        return returnMatrix.asMatrix()


    def customParentConstraint(self, parent, object, traslationOffsetFlag = True, rotationOffsetFlag=True, translationFlag = True, rotationFlag = True, scaleFlag = True):
        # Getting object parent
        objParent = fn.getParent(object)
        # Create Constraint Node
        asAnimationBinderNode = mc.createNode("asParentConstraint")
        if (traslationOffsetFlag == True or rotationOffsetFlag == True):
            localOffset = self.getLocalOffset(parent, object, translationOffsetFlag = traslationOffsetFlag, rotationOffsetFlag= rotationOffsetFlag)
            mc.setAttr(asAnimationBinderNode+".localOffset", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
        mmod.connectAttr(parent+".worldMatrix", asAnimationBinderNode+".parentWorldMatrix")
        mmod.connectAttr(objParent+".worldInverseMatrix", asAnimationBinderNode+".parentInverseMatrix")
        if (rotationFlag):
            mmod.connectAttr(asAnimationBinderNode+".outRotation", object+".rotate")
        if (translationFlag):
            mmod.connectAttr(asAnimationBinderNode+".outTranslation", object+".translate")
        if (scaleFlag):
            mmod.connectAttr(asAnimationBinderNode+".outScale", object+".scale")

    def gettingFlags(self):
        translationOffset = mc.checkBox ( self.translationOffsetCB, q=True, v=True)
        rotationOffset = mc.checkBox ( self.rotationOffsetCB, q=True, v=True)
        retargetTranslation = mc.checkBox ( self.retargetTranslationCB, q=True, v=True)
        retargetRotation = mc.checkBox ( self.retargetRotationCB, q=True, v=True)
        retargetScale = mc.checkBox ( self.retargetScaleCB, q=True, v=True)
        alignCtrlTranslation = mc.checkBox ( self.alignCtlTranslationCB, q=True, v=True)
        alignCtrlRotation = mc.checkBox ( self.alignCtlRotationCB, q=True, v=True)
        return translationOffset, rotationOffset, retargetTranslation, retargetRotation, retargetScale, alignCtrlTranslation, alignCtrlRotation


    def complexRetargeting(self, *args):
        print "complexBind"
        # GETTING FLAGS
        translationOffset, rotationOffset, retargetTranslation, retargetRotation, retargetScale, alignCtrlTranslation, alignCtrlRotation = self.gettingFlags()       
        # GET SELECTION LIST 
        parentObject = mc.ls(sl=True, an=True)[0]
        childObject = fn.getParent(mc.ls(sl=True, an=True)[1])
        # CREATING CTRL
        # GuideObject
        guide = mmod.transform(parent=fn.getParent(parentObject))
        fn.align(parentObject, guide)
        # Checking Alignment
        if (alignCtrlTranslation):
            mc.delete(mc.pointConstraint(childObject, guide))
        translationCtrl = rigFn.constructCTL(guide, side="C", name="translationManipulator", parent=parentObject, ctrlShape = 3)
        # Creating Child Control
        if (alignCtrlRotation):
            mc.delete(mc.orientConstraint(childObject, guide))
        rotationCtrl = rigFn.constructCTL(guide, side="C", name="RotationManipulator", parent=translationCtrl, ctrlShape = 2)
        mc.delete(guide)

        # CONSTRAINING CONTROL
        self.customParentConstraint(parentObject, fn.getParent(fn.getParent(translationCtrl)), True, True, True, True, True)
        # CONSTRAINING CHILD
        self.customParentConstraint(rotationCtrl.name, childObject, translationOffset, rotationOffset, retargetTranslation, retargetRotation, retargetScale)

    def simpleRetargeting(self, *args):
        print "simpleBind"
        # GETTING FLAGS
        translationOffset, rotationOffset, retargetTranslation, retargetRotation, retargetScale, alignCtrlTranslation, alignCtrlRotation = self.gettingFlags()              
        # GET SELECTION LIST 
        parentObject = mc.ls(sl=True, an=True)[0]
        childObject = fn.getParent(mc.ls(sl=True, an=True)[1])
        # CREATING CTRL
        # GuideObject
        guide = mmod.transform(parent=parentObject)
        # Checking Alignment
        if (alignCtrlRotation):
            mc.delete(mc.orientConstraint(childObject, guide))
        if (alignCtrlTranslation):
            mc.delete(mc.pointConstraint(childObject, guide))
        translationCtrl = rigFn.constructCTL(guide, side="C", name="name", parent=parentObject, ctrlShape = 2)
        mc.delete(guide)
        # CREATING CONSTRAINT
        self.customParentConstraint(translationCtrl.name, childObject, translationOffset, rotationOffset, retargetTranslation, retargetRotation, retargetScale)
        
    def findInbetween(self, timeArray, valueArray, start, end):
        maxDist = 0
        maxDistFrame = 0
        errorRate = 0.05
        line = lineEquation(start, end )
        for i, (frame, value) in enumerate(zip(timeArray, valueArray)):
            dist = linePointDistance(line, [frame, value])
            if (dist> maxDist):      
                maxDist = dist
                maxDistFrame = i

        if (maxDist < errorRate):
                return 0 
        return maxDistFrame

    def customFiltering(self, curve, itterations, timeArray, valueArray):
        # FOR VISUALIZATION
        # KEEP START AND END
        mc.cutKey(curve, t=(timeArray[1],timeArray[-2]))
        # ITTERATION 
        for i in range (itterations):
            # GETTING CURRENT FRAMES
            currentTimeArray, currentValueArray = self.getAnimationData(curve)
            for index in range (len(currentTimeArray)-1): 
                start = int(currentTimeArray[index])-1
                end = int(currentTimeArray[index+1])
                inbetweenFrame = self.findInbetween(timeArray[start:end], valueArray[start:end], 
                                                    [currentTimeArray[index], currentValueArray[index]], 
                                                    [currentTimeArray[index+1], currentValueArray[index+1]])
                if (inbetweenFrame != 0 ):
                        frame = mc.setKeyframe(curve, value = valueArray[start + inbetweenFrame], time=timeArray[start + inbetweenFrame])
                else:
                        print "no Inbetween"    

    def curveSimplification(self, *args):
        print "simplify"
        # GET NUMBER OF ITTERATIONS
        itter = mc.intSliderGrp(self.itterationsSlider, q=True, value=True)
        # GETTING CURVE SELECTION
        selectedCurve = cmds.keyframe(q=True, sl=True, n=True)
        if (self.animationCurve !=None):
            if (self.animationCurve != selectedCurve):
                # GETTING ANIMATION
                timeArray, valueArray = self.getAnimationData(self.animationCurve)
                self.timeArray = timeArray
                self.valueArray = valueArray
                self.animationCurve = selectedCurve
        if (self.animationCurve == None):
            self.animationCurve = selectedCurve
            # GETTING ANIMATION
            timeArray, valueArray = self.getAnimationData(self.animationCurve)
            self.timeArray = timeArray
            self.valueArray = valueArray
        print self.animationCurve
        self.customFiltering(self.animationCurve, itter, self.timeArray, self.valueArray)
                
    
    def getAnimationData(self, attribute):
        print attribute
           
        numKeyframes = mc.keyframe(attribute, query=True, keyframeCount=True)

        if (numKeyframes > 0):
            timeArray = mc.keyframe(attribute, query=True, index=(0,numKeyframes), timeChange=True)
            valueArray = mc.keyframe(attribute, query=True, index=(0,numKeyframes), valueChange=True)  
        return timeArray, valueArray

    def animationGui(self):
        if mc.window(self.windowName, exists=True):
            mc.deleteUI(self.windowName, window=True)
        mc.window(self.windowName, title=self.windowName, widthHeight=(self.windowWidth, self.windowHeight), resizeToFitChildren=1)
        form = mc.formLayout()
        tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        mc.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
        
        ##############################################################################
        ##########################  Animation Retargeting   ##########################
        animationRetargetingTab = mc.rowColumnLayout()

        
        ########################################################################
        ##########################  BINDING OPTIONS   ##########################
        mc.frameLayout( label='Binding', collapsable=True, width=self.windowWidth )

        mc.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 150), (2, 20), (3, 150)])
        self.translationOffsetCB = mc.checkBox("Translation Offset", v=True); mc.separator(vis=False)
        self.rotationOffsetCB = mc.checkBox("Rotation Offset",  v=True); 
        self.retargetTranslationCB = mc.checkBox("Retarget Translation",  v=True); mc.separator(vis=False)
        self.retargetRotationCB = mc.checkBox("Retarget Rotation",  v=True)
        self.retargetScaleCB = mc.checkBox("Retarget Scale",  v=True); mc.separator(vis=False); mc.separator(vis=False)

        self.alignCtlTranslationCB = mc.checkBox("Align Ctl Translation",  v=True); mc.separator(vis=False)
        self.alignCtlRotationCB = mc.checkBox("Align Ctl Rotation",  v=True)
        

        ##########################  BINDING OPTIONS   ##########################
        ########################################################################
        mc.setParent( '..' )
        mc.setParent( '..' )
        #########################################################################
        ##############################  COMMANDS   ##############################
        mc.frameLayout( label='commands', collapsable=True, width=self.windowWidth )
        mc.rowColumnLayout(numberOfColumns=1)
        mc.button("Simple Retargeting", width = self.windowWidth, bgc=[0.3, 0.3, 0.3], command=partial(self.simpleRetargeting))
        mc.button("Complex Retargeting", width = self.windowWidth, bgc=[0.3, 0.3, 0.3], command=partial(self.complexRetargeting))
        mc.button("Aim Retargeting", width = self.windowWidth, bgc=[0.3, 0.3, 0.3])

        ##############################  COMMANDS   ##############################
        #########################################################################
        mc.setParent( '..' )
        mc.setParent( '..' )
        ##########################################################################
        ##########################  SIMPLE RETARGETING   ##########################
        mc.frameLayout( label='Simple Retargeting', collapsable=True, width=self.windowWidth )
        mc.rowColumnLayout(numberOfColumns=1)
        mc.button("DirectConnection: ", width = self.windowWidth)
        mc.button("ConstraintConnection", width = self.windowWidth)

        ##########################  SIMPLE RETARGETING   ##########################
        ###########################################################################


        ##########################  Animation Retargeting   ##########################
        ##############################################################################
                
        cmds.setParent( '..' )
        cmds.setParent( '..' )

        cmds.setParent( '..' )

        ##############################################################################
        ##########################  Curve Simplification   ##########################
        curveSimplificationTab = mc.rowColumnLayout(cw = [1, 100])

        ########################################################################
        ##########################  BINDING OPTIONS   ##########################
        mc.frameLayout( label='Filtering', collapsable=True, width=self.windowWidth )
        # mc.rowColumnLayout(numberOfColumns=3, columnWidth=[(1, 150), (2, 20), (3, 150)])

        # mc.text("Itterations");mc.separator(vis=False)
        self.itterationsSlider = mc.intSliderGrp("Itterations", l="Itterations", min=0, max=20, field=True, width=100, cal=[(1, "left")], cc=partial(self.curveSimplification))

        ##########################  DOCKING   ##########################

        # if mc.dockControl(self.dockControl, exists=True):
        #     mc.deleteUI(self.dockControl, control=True)
        # allowedAreas = ['right', 'left']
        # mc.dockControl( self.dockControl, area='right', content=self.windowName, allowedArea=allowedAreas )
        # # cmds.evalDeferred("cmds.dockControl('%s', e=True, r=True)" % self.dockCnt)  # for fuck sake Maya, raise the dock yourself!!
                
        ##########################  DOCKING   ##########################
        cmds.tabLayout( tabs, edit=True, tabLabel=( (animationRetargetingTab, 'Animation Retargeting'), (curveSimplificationTab, 'CurveFiltering')))

        mc.showWindow(self.windowName)
        mc.window(self.windowName, e=True, widthHeight=(self.windowWidth, self.windowHeight), resizeToFitChildren=1)


def cubeTesteScene():
    mc.file(new=True, f=True)
    path = "D:/Bournemouth University/CVA_Y3/Innovations/tests/"
    fn.loadLatestFile(path)
def customParentConstraint(parent, object):
    # Getting object parent
    objParent = fn.getParent(object)
    print objParent
    # Create Constraint Node
    asAnimationBinderNode = mc.createNode("asParentConstraint")
    localOffset = fn.getLocalOffset(objParent, object)
    mc.setAttr(asAnimationBinderNode+".localOffset", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
    mmod.connectAttr(parent+".worldMatrix", asAnimationBinderNode+".parentWorldMatrix")
    mmod.connectAttr(objParent+".worldInverseMatrix", asAnimationBinderNode+".parentInverseMatrix")
    mmod.connectAttr(asAnimationBinderNode+".outRotation", object+".rotate")
    mmod.connectAttr(asAnimationBinderNode+".outTranslation", object+".translate")
    mmod.connectAttr(asAnimationBinderNode+".outScale", object+".scale")
def simpleAnim():
    mc.file(new=True, f=True)
    path = "D:/Bournemouth University/CVA_Y3/Innovations/raw/simpleAnim.0000.ma"
    mc.file( path, i= True, type= "mayaAscii", usingNamespaces= False, f=True)
def copyAnimation (source = None, target=None):
    # GET ANIMATION RANGE
    # !!!!!!!!!! GET ANIMATION RANGE ON SELECTED OBJECT !!!!!!!!!!
    animationEnd = mc.playbackOptions(q=True, max=True)
    animationStart = mc.playbackOptions(q=True, min=True)
    for frame in range (int(animationStart),int(animationEnd)):
        mc.currentTime(frame, update=True)
        translate = mc.xform(source, q=True, t=True, ws=True)
        rotation = mc.xform (source, q=True, ro=True, ws=True )
        mc.xform(target, ws=True, ro= rotation, t = translate)
        mc.setKeyframe(target, time=frame)


def recreateAnimation(sourceAnimation=None):
    # Copying animation from given joint to a sphere
    testSphere = mc.polyCone(name="testObject")
    if sourceAnimation!=None:
        copyAnimation(sourceAnimation, testSphere)

    return testSphere[0]
        
#####################################################################################
#                       Curve Simplifier
#####################################################################################
def getMObject(objName):
    selectionList = om.MSelectionList()
    try: 
        print "try"
        selectionList.add(objName)
        mObj = om.MObject()
        selectionList.getDependNode(0, mObj)
        return mObj
    except:
        print "except"
        return None
    
  
def getPlug(obj, attr):
    ''' returns node's plug '''
    self_mObject =getMObject(obj)
    dependencyNode =om.MFnDependencyNode(self_mObject)
    try:
        plug = dependencyNode.findPlug(nodeName)
        return plug
    except:
        return None
def curveSimplifier (object = None, dimension=".rotateZ"):
    if (object!=None):

        # Create MFnAnimCurve Object
            
        err = 0.1
        # CREATE TEMPORARY OBJECT
        tempSphere = mc.polyCone(name="temporaryObject")[0]
        objMObj = getMObject(object)
        animCurve = omAnim.MFnAnimCurve(objMObj)

        # tempSphereAttr = getPlug(object, "rotateZ")
        # createAnimCurve = animCurve.create(tempSphereAttr, omAnim.MFnAnimCurve.kAnimCurveTL)
        # CREATE START END LINE
        # Start
        curve = mc.selectKey(object, at = dimension)
    




# customParentConstraint("customNodeConstraint|C_parentCube00_GRP1|C_parentCube01_CTL1", "customNodeConstraint|C_constraintCubeCustomNode00_GRP1")
# simpleAnim()
# testObj = recreateAnimation(sourceAnimation = "Bip01FBXASC032RFBXASC032Forearm")
# cubeTesteScene()
animationGUIWindoe = animationGUI()
# curveSimplifier(object = testObj)