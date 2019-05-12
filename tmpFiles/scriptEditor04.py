import maya.OpenMaya as om
import maya.cmds as mc


# # FINGER

# import maya.OpenMaya as om
# import shutil 
# import os 
# import sys
# import mayaModule as mmod
# import functions as fn
# import pipeline 
# import asNodes as asNode
# import mayaNode as mNode
# import blendFKIK as blendFKIK
# import ribbon
# import rigFn as rigFn
# import mayaNode as node

# import controlFn as ctlFn
# class finger(object):
#     globalCtrl=None
#     def __init__(self, jntHierarchy, fingerName="finger", side="C", parent=None, hook=None, worldUpVector=""):
#         '''
#         NAMES
#         fingerName ={thumb, index, middle, ring, pinky}


#         1. HIERARCHY STRUCTURE
#             fingerName_GRP
#                 metacarpal_GRP>OFS>JNT
#                     phalangeA00_GRP>OFS>CTL>JNT
#                         phalangeB00_GRP>OFS>CTL>JNT
#                             phalangeC00_GRP>OFS>CTL>JNT
                         
#         '''

#         # GLOBALS
#         self.side = side
#         self.parent = parent
#         self.hook = hook
#         self.worldUpVector = worldUpVector
#         mmod.resetCount()

#         metacarpalName = fingerName+"Metacarpal"
#         phalangeName = [fingerName+"ProximalPhalange", fingerName+"MiddlePhalange", fingerName+"DistalPhalange"] 
#         guidJntList = mc.listRelatives(jntHierarchy, ad=True); guidJntList.reverse()
#         fingerBaseJnt=[]

#         aimVector = [1, 0, 0]
#         upVector = [0, 1, 0]
        
#         # FINGER CONTROLLER COLOR
#         if (self.side == "L"):
#             self.ctlColor = 18
#         if (self.side == "R"):
#             self.ctlColor = 20

#         # CREATING HIERARCHY
#         self.fingerGRP = mmod.transform(side=side, name=fingerName, type="GRP", parent=parent)
#         # worldUpVector
        
#         # GLOBAL CTRL
#         if (fingerName=="pinky"):
#             finger.globalCtrl = rigFn.constructCTL(jntHierarchy, side=side, name=metacarpalName, parent=self.fingerGRP)
#             finger.globalCtrl.setColor(self.ctlColor)
#             #metaJntA = fn.getChildren(self.globalCtrl.name)[1]
#             #fingerBaseJnt.append(metaJntA)

#         metaJntA = rigFn.constructJNT(jntHierarchy, side=side, name=metacarpalName, parent=self.fingerGRP)
#         fingerBaseJnt.append(metaJntA.name)

#         # METACARPAL JNT        
#         metaJntB = mmod.joint(side=side, name=metacarpalName, parent=metaJntA)
#         metaJntB.translateX=mc.xform(guidJntList[0], q=True, r=True, t=True)[0]
#         metaGrp = mmod.transform(side=side, name=metacarpalName, parent=fn.getParent(metaJntA), type="GRP")
#         mc.parent(metaJntA, metaGrp)
        
#         # PHALANGES JNT
#         for i, jnt in enumerate(guidJntList[:-1]):
#             phalangeCTL = rigFn.constructCTL(jnt, side=side, name=phalangeName[i], parent=fn.getParent(metaJntA) if i==0 else phalangeCTL)
#             fingerBaseJnt.append(mc.listRelatives(phalangeCTL, c=True, typ="joint")[0])
#             jntB = mmod.joint(side=side, name=phalangeName[i], parent=fingerBaseJnt[i+1])
#             phalangeCTL.setColor(self.ctlColor)

#             # AIM CONSTRAINTS
#             # Creating WorldUpObject
#             worldUpObj = mmod.transform(side=self.side, name=fingerName+str(i)+"WorldUpObject", parent=fn.getParent(fingerBaseJnt[i]))
#             fn.snapTool(fingerBaseJnt[i], worldUpObj)
#             mc.aimConstraint(fingerBaseJnt[i+1], fingerBaseJnt[i], aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=worldUpObj)

            
#             # JOINT STRETCHING
#             distanceBetweenNode = mc.createNode("distanceBetween", name=side+"_distance"+fingerName+str(i)+"_DST")
#             mc.connectAttr(fingerBaseJnt[i]+".worldMatrix", distanceBetweenNode+".inMatrix1")
#             mc.connectAttr(fingerBaseJnt[i+1]+".worldMatrix", distanceBetweenNode+".inMatrix2")

#             # Scalingby global scale
#             divide = mNode.multiplyDivide(side=self.side, name=fingerName+str(i)+"GlobalScale")
#             worldTransformation = mNode.decomposeMatrix(side=self.side, name = "rootGlobalTransformation")
#             mmod.connectAttr(self.hook+".worldMatrix", worldTransformation.getInputMatrix())
#             mmod.connectAttr(distanceBetweenNode+".distance", divide.name+".input1X")
#             divide.operation = 2
#             mmod.connectAttr(worldTransformation.getOutputScale(), divide.getInput2())
           
#             # Minus operation
#             minusNode = mc.createNode("plusMinusAverage", name=side+"_subtract"+fingerName+str(i)+"_PMA")
#             mc.setAttr(minusNode+".operation", 2)
#             mc.connectAttr(divide.name+".outputX", minusNode+".input1D[0]")
#             mc.connectAttr(fingerBaseJnt[i+1]+".radius", minusNode+".input1D[1]")

#             # Connecting Translate X
#             mc.connectAttr(minusNode+".output1D", fn.getChildren(fingerBaseJnt[i])[0]+".translateX")


#             # POSITIONING END JNT
#             if (jnt==guidJntList[-2]):
#                 translateX = mc.getAttr(guidJntList[-1]+".translateX")
#                 mc.setAttr(fn.getChildren(fingerBaseJnt[-1])[0]+".translateX", translateX)


#         self.fingerJntChain = fingerBaseJnt

#         # DELETING GUIDES
#         mc.delete(jntHierarchy)

# side=["L", "R"]
# for s in side:
#     fingerObj = finger(s+"_thumb00_JNT", fingerName="thumb", side=s, parent=s+"_handFingers*_GRP", hook="C_root00_JNT")

def getSelectedComponentsPositions ():
    ''' 
    This function loops though all the selected objects and returns the positions of the selected points
    
    ReturnType: om.MPointArray
    '''

    # RETURN ARRAY
    pointList = om.MPointArray()
        
    # Create Enpty Seelction List
    selectionList = om.MSelectionList()

    # Assign Active Selection List
    om.MGlobal.getActiveSelectionList(selectionList)

    # Creating a Selection Itter
    selectionItter = om.MItSelectionList(selectionList)

    selectionItter.reset()
    while (selectionItter.isDone() == False ):
        # Get the path of the selected obj
        dagPath = om.MDagPath()
        # Get Component List
        componentList = om.MObject()

        
        selectionItter.getDagPath(dagPath, componentList )
        # DependencyNode
        dependencyNode = om.MFnDependencyNode (dagPath.node())

        # Going through the components
        if (componentList.isNull() ==False):
            # Geometry Iterator
            geomItter = om.MItGeometry (dagPath, componentList)

            # Loop through points
            while (geomItter.isDone()!=True):
                # Get WorldSpace Position
                point = om.MPoint(geomItter.position(om.MSpace.kWorld))
                geomItter.next()
                # print point.x, point.y, point.z
                pointList.append(point)


        selectionItter.next()

    return pointList


def getBoundingBox():
    pointList = om.MPointArray()
    pointList = getSelectedComponentsPositions()

    # Loop through points and find minX, minY, minZ and maxX, maxY, maxZ
    # minCorner  = om.MPoint()
    # maxCorner  = om.MPoint()
    
    minCorner = [ pointList[0].x, pointList[0].y, pointList[0].z]
    maxCorner =  [ pointList[0].x, pointList[0].y, pointList[0].z]

    for i in range (1, pointList.length()):
        point = pointList[i]
        if (point.x < minCorner[0]):
            minCorner[0]= point.x
        if (point.y < minCorner[1]):
            minCorner[1] = point.y
        if (point.z < minCorner[2]):
            minCorner[2] = point.z
        if (point.x > maxCorner[0]):
            maxCorner[0] = point.x
        if (point.y > maxCorner[1]):
            maxCorner[1] = point.y
        if (point.z > maxCorner[2]):
            maxCorner[2] = point.z

    boundingBox = om.MBoundingBox (om.MPoint(minCorner[0], minCorner[1], minCorner[2]), om.MPoint(maxCorner[0], maxCorner[1], maxCorner[2]))
    return boundingBox


def createJoint ():

    boundingBox = getBoundingBox()
    center = boundingBox.center()
    
    mc.select (clear= True)
    jnt = mc.joint (p=[center.x, center.y, center.z])
        
# createJoint()

def matchingAnimation(extraAttributes=[]):
    '''
    matching animation from first selected ctrl to second

    '''

    selection = mc.ls(sl=True)
    if (len(selection)!=2):
        mc.warning( "Selection needs to be equal to 2. First element is the object from which the animation will be copied and second object is the one to which the animation will be coppied to " ) 
        return

    animObj = selection[0]
    object = selection[1]

    # GETTING KEY FRAMES
    numKeyframes = mc.keyframe(animObj, query=True, keyframeCount=True)
    if (numKeyframes > 0 ):
        keyFramesArray = mc.keyframe(animObj, query=True, index=(0,numKeyframes), timeChange=True)

    # MATCHING ANIMATION
    # 1. Looping through keyFrames
    for frame in keyFramesArray:
        # 2. Set current time
        mc.currentTime (frame)
        # 3. Match Translation
        # mc.xform (object, t=mc.xform (animObj, q=True, t=True, ws=True), ws=True)
        # 4. Matching Rotation
        mc.xform (object, ro=mc.xform (animObj, q=True, ro=True, ws=True), ws=True)

        # Matching Other Attributes
        if (len(extraAttributes)!=0):
            for attr in extraAttributes:
                mc.setAttr(object+"."+attr, mc.getAttr(animObj+"."+attr))

        # Set Key
        mc.setKeyframe(object, time=frame)


# import mayaModule as mmod
# import rigFn as rigFn
# import functions as fn
# import jawModule 
# import ribbon as ribbon

# def faceRig():
#     # mmod.resetCount()
#     # # CENTER EYEBROW
#     # ctrl = rigFn.constructCTL("C_eyeBrow00_JNT", name="eyebrowCenter", parent="C_headTop00_JNT", ctrlScale=1, ctrlShape=0)

    
#     # # Head Top
#     # rigFn.constructCTL("C_headTop00_JNT", side="C", name="headTop", parent="C_head00_JNT", ctrlScale=1, ctrlShape=0)
    
#     # # Head Base
#     # rigFn.constructCTL("C_headBottom00_JNT", side="C", name="headBase", parent="C_head00_JNT", ctrlScale=1, ctrlShape=0)
    
#     # Jaw
#     # jaw = jawModule.jaw(side="C", name="jaw", jawJnt="C_jaw00_JNT", root="C_headBase01_CTL")
#     # jaw = rigFn.constructCTL("C_bindJaw00_JNT3", side="C", name="jaw", parent="C_headBase01_CTL", ctrlScale=1, ctrlShape=0)

#     # Eye Aim Center
#     # eyeAimCenter =  rigFn.constructCTL("C_eyeAim00_JNT", side="C", name="aimEye", parent="C_root00_JNT", ctrlScale=1, ctrlShape=5)
#     # # Space Switch
#     # eyeAimCenter.createSpaceSwitch()
#     # eyeAimCenter.addSpaceSwitch (spaceName = "head", parentObject = "C_head00_CTL")
#     # eyeAimCenter.addSpaceSwitch (spaceName = "COG", parentObject = "C_COG00_CTL") 
#     # eyeAimCenter.addSpaceSwitch (spaceName = "Chest", parentObject = "C_chest04_CTL")

    
#     # EYEBROWS
#     # Create guide Group
#     # eyeBrowsGlobal = mmod.transform(name="eyebrowsGlobal", type="GRP", parent="C_rig00_GRP")
#     # eyeBrowsGuidesGroup = mmod.transform(name="eyebrowsGuides", type="GRP", parent = eyeBrowsGlobal)

#     # eyeBrowsRoot = mmod.transform(name="localEyebrows", type="GRP", parent="C_headTop00_JNT")
    

#     # side = ["L", "R"]
#     # for s in side:

#     #     # Local Eyes
#     #     # localEye = rigFn.constructCTL(s+"_eye00_JNT", side=s, name="localEye", parent="C_headTop00_JNT", ctrlScale=1, ctrlShape=0)
#     #     # Eye Aim
#     #     eyeAim = rigFn.constructCTL(s+"_eyeAim00_JNT", side=s, name="aimEye", parent=eyeAimCenter, ctrlScale=1, ctrlShape=0)
        
#         # EYE BROWS
#         # Create Guide Structures
#         # eyebrowsGuides =[]
#     #     for guide in fn.getChildren(s+"_eyeBrow00_GRP"):
#     #         eyebrowsGuides.append(rigFn.constructCTL(guide, side=s, name="eyebrowGuide", parent="C_headTop00_JNT", ctrlScale=1, ctrlShape=6))
#     #         # mc.parent(eyebrowsGuides[-1], eyeBrowsGuidesGroup)
#     #     ribbonStruct = ribbon.ribbon(side=s, name="eyeBrow", guides=eyebrowsGuides, numberOfJoints=5, revolveVector= [0, 1, 0], parent=eyeBrowsGuidesGroup, root=eyeBrowsRoot)

#     # mc.delete("*_eyebrowGuide*_JNT")


#     # LIPS Controls
#     # middleCtr = rigFn.constructCTL("upperMiddle", side="C", name="upperLip", parent="C_headBase01_CTL", ctrlScale=1, ctrlShape=5)

#     # EyeLids
#     list = mc.ls(sl=True)
#     for jnt in list:
#         rigFn.constru
   


def copyAnimation(originalString, replaceString):
    selctionList = mc.ls(sl=True)

    # if (len(selection)!=2):
    #     mc.warning( "Selection needs to be equal to 2. First element is the object from which the animation will be copied and second object is the one to which the animation will be coppied to " ) 
    #     return

    # animObj = selection[0]
    # object = selection[1]

    # GETTING KEY FRAMES
    numKeyframes = mc.keyframe(selctionList[0], query=True, keyframeCount=True)
    if (numKeyframes > 0 ):
        keyFramesArray = mc.keyframe(selctionList[0], query=True, index=(0,numKeyframes), timeChange=True)

    # MATCHING ANIMATION
    # 1. Looping through keyFrames
    for frame in keyFramesArray:
        # 2. Set current time
        mc.currentTime (frame)
        for control in selctionList:

            object = control.replace(originalString, replaceString)
                
            # 3. Match Translation
            # mc.xform (object, t=mc.xform (control, q=True, t=True, ws=True), ws=True)
            # 4. Matching Rotation
            mc.xform (object, ro=mc.xform (control, q=True, ro=True, ws=True), ws=True)

        # Set Key
        mc.setKeyframe(object, time=frame)

# copyAnimation("s2AnimatioTest:diana00_0018", "diana00_0022")
# faceRig()

matchingAnimation()