
''' 
Ana Maria Savastre
Bournemouth University 

Major Project: Richest Girl in Town

Character: Diana

'''

import maya.cmds as mc
import majorProjectCharacter as mjChr 
import loadFn
import socket


import maya.OpenMaya as om
import shutil 
import os 
import sys
import mayaModule as mmod
import functions as fn
import pipeline 
import asNodes as asNode
import mayaNode as mNode
import blendFKIK as blendFKIK
import ribbon
import rigFn as rigFn
import mayaNode as node

import controlFn as ctlFn


# Body Modules
import spineModule as spineMod
import neckModule as neckMod
import armModule as armMod
import scapulaModule as scapulaMod
import legModule as legMod
import footModule as footMod
import tailModule as tailMod
import handModule as handMod
import clavicleModule as clavicleMod
# Face Module
import jawModule as jawMod
# GLOBALS
hostName = socket.gethostname()

if (hostName == "DESKTOP-4NJ3EJ0"):
    projectEnv = "C:/Users/anama/Desktop/MajorProject/Production/MPJ_MASTER/assets/character/"
if (hostName == "DESKTOP-CM0E2QL"):
    projectEnv = "C:/Users/Kari Noriy/Desktop/Ana/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-PQV0HOV"):
    projectEnv = "C:/Users/AnaMaria/Documents/asRigging/projects/masterClass/"

controlShapesPath = "D:/Bournemouth University/asRigging/controlShapes"


import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import controlFn as ctlFn

import blendFKIK as blendFKIK
import ribbonLimbs as ribbonLimbs




class foot(object):
    def __init__(self, side="C", footJnt=None, root=None, parent=None, hook=None):
        ''' 
        root = leg() object
        parent = parent bind jnt (FK foot)
        '''
        # self
        self.side = side
        self.footJnt = footJnt
        self.legRoot = root
        self.ankleCtrl = root.effectorCtrl
        self.parent = parent
        self.root = root
        self.hook = hook
        self.footSegments = ["Ankle", "Tarsals", "Toes"]
        self.footName="foot"
        
        if (footJnt):
            # FK Foot            
            footJNTList = fn.descendentsList(root=footJnt)
            self.footJNTList = []
            for elem in footJNTList:
                self.footJNTList.append(elem)
        

            self.FKfoot_setUp(footJNTList=footJNTList, parent=self.parent)
            # FOOT ROLL
            self.footRoll_setUp(footJNTList=footJNTList, parent=root.segmentGRP)

            # CONSTRAINING FOOT TO  FK ANKLE (temporary done with orient constraint)
            orientConstraint =mc.orientConstraint(self.legRoot.FKjntChain[-1], fn.getParent(fn.getParent(self.footFKJnt[0])), mo=True)[0]
            ocWeightAlias = mc.orientConstraint(orientConstraint, q=True, wal=True)[0]
            mmod.connectAttr( self.legRoot.reverseBlend.getOutput(), orientConstraint+"."+ocWeightAlias)

            # # CONNECTING FK ANKLE TO IK ANKLE
            mmod.connectAttr(self.ankleCtrl.name+".rotate", self.ikAnkleCtrlConnectionGrp.name+".rotate")
            # parentConstraint = mc.parentConstraint(self.ankleCtrl, fn.getParent(self.footFKJnt[0]), mo=True)[0]
            # pcWeightAlias = mc.parentConstraint(parentConstraint, q=True, wal=True)[0]
            # mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", parentConstraint+"."+pcWeightAlias)
            # orientConstraint =mc.orientConstraint(self.ankleCtrl, fn.getParent(fn.getParent(self.footFKJnt[0])), mo=True)[0]
            # ocWeightAlias = mc.orientConstraint(orientConstraint, q=True, wal=True)[1]
            # mmod.connectAttr( self.legRoot.settingCtl.name+".fkIkBlend", orientConstraint+"."+ocWeightAlias)
            # mmod.connectAttr()
            # Making Scaleable
            mmod.connectAttr(fn.getParent(self.hook)+".scale", fn.getParent(self.footFKJnt[0])+".scale")
            
            # Connecting Ankle Twist to Ribbon Leg
            self.twistLeg()

            # ANKLE - Adding Extra Attributes 
            self.ankleAttributes()

            # DELETING GUIDES
            mc.delete(footJnt)

    def ankleAttributes(self):
        '''
        Adding extra attributes on ankle control

        LEG MOVEMENT
            legTwist
        FOOT ROOL CONFIGURATION
            tarsalLock
            straighten
        FOOT MOVEMENT
            toeRotation
            tarsalRotation
            HeelTwist
            ToeTwist
            TarsalTwist???

        '''
        # GLOBAL
        ctrl = self.legRoot.effectorCtrl
        twistAttr = self.legRoot.ikHandle+".twist"

        # LEG MOVEMENT
        # legTwist
        ctrl.addAttr( longName='legTwist', attrType='double' )     
        mmod.connectAttr(ctrl.name+".legTwist", twistAttr)

        # FOOT ROOL CONFIGURATION
        # tarsalLock
        tarsalLock = ctrl.addAttr( longName='tarsalLock', softMinValue=-1.7, defaultValue=0.34, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        # Set Tarsal Lock Attribute 
        mc.setAttr(ctrl.name+".tarsalLock", mc.getAttr(self.animParameters.name+".tarsalLock"))
        # Connect Attr
        mmod.connectAttr(ctrl.name+".tarsalLock", self.animParameters.name+".tarsalLock")    

        # straighten
        straighten = ctrl.addAttr( longName='straighten',  softMinValue=-15, defaultValue=1.5, softMaxValue=15, attrType="double", keyable=True) 
        # Set Attr Value
        mc.setAttr(ctrl.name+".straighten", mc.getAttr(self.animParameters.name+".straighten"))
        mmod.connectAttr(ctrl.name+".straighten", self.animParameters.name+".straighten")

        # FOOT MOVEMENT
        # heelRotation
        # attrName = 'heelRotation'
        # attribute = self.configParameters.name+".toeRest"
        # toeRotation = ctrl.addAttr(longName=attrName, softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        # addNode = mNode.addDoubleLinear(side=self.side, name=attrName+"AddToeRotToRestVal")
        # mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
        # mc.setAttr(addNode.getInput2(), mc.getAttr(attribute))
        # mmod.connectAttr(addNode.getOutput(), attribute)
        # toeRotation
        attrName = 'toeRotation'
        attribute = self.configParameters.name+".toeRest"
        toeRotation = ctrl.addAttr(longName=attrName, softMinValue=-3.14, defaultValue=0, softMaxValue=0, attrType="doubleAngle", keyable=True)
        addNode = mNode.addDoubleLinear(side=self.side, name=attrName+"AddToeRotToRestVal")
        mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
        mc.setAttr(addNode.getInput2(), mc.getAttr(attribute))
        mmod.connectAttr(addNode.getOutput(), attribute)
        # tarsalRotation
        attrName = 'tarsalRotation'
        attribute = self.configParameters.name+".tarsalRest"
        toeRotation = ctrl.addAttr(longName=attrName, softMinValue=0, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        addNode = mNode.addDoubleLinear(side=self.side, name=attrName+"AddToeRotToRestVal")
        mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
        mc.setAttr(addNode.getInput2(), mc.getAttr(attribute))
        mmod.connectAttr(addNode.getOutput(), attribute)
        # heelTwist
        attrName = 'heelTwist'
        attribute = self.footRollJnt[0].name+".rotateY"
        toeRotation = ctrl.addAttr(longName=attrName, softMinValue=-5, defaultValue=0, softMaxValue=5, attrType="doubleAngle", keyable=True)
        addNode = mNode.addDoubleLinear(side=self.side, name=attrName+"AddToeRotToRestVal")
        mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
        mc.setAttr(addNode.getInput2(), mc.getAttr(attribute))
        mmod.connectAttr(addNode.getOutput(), attribute)
        # toeTwist
        attrName = 'toeTwist'
        attribute = self.footRollJnt[1].name+".rotateY"
        toeRotation = ctrl.addAttr(longName=attrName, softMinValue=-5, defaultValue=0, softMaxValue=5, attrType="doubleAngle", keyable=True)
        addNode = mNode.addDoubleLinear(side=self.side, name=attrName+"AddToeRotToRestVal")
        mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
        mc.setAttr(addNode.getInput2(), mc.getAttr(attribute))
        mmod.connectAttr(addNode.getOutput(), attribute)

    def twistConnection(self, targetParent, object):
        objParent = fn.getParent(object)
        # Matrix Mult
        side = fn.concat_str(str1 = object, s1_begin=0, s1_end=len(object)-1 )
        matrix = mNode.multMatrix(side=side, name="transformationMatrix")
        # GETTING LOCAL OFFSET
        localOffset = fn.getLocalOffset(objParent, object)
        mc.setAttr(matrix.name+".matrixIn[0]", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")


        mmod.connectAttr(targetParent+".worldMatrix", matrix.name+".matrixIn[1]")
        mmod.connectAttr(objParent+".worldInverseMatrix", matrix.name+".matrixIn[2]")
        decomposeMatrix = mNode.decomposeMatrix(side=side, name="transformation")
        mmod.connectAttr(matrix.getMatrixSum(), decomposeMatrix.getInputMatrix())
        mmod.connectAttr(decomposeMatrix.name+".outputRotateX", object+".rotateX")
    def twistLeg(self):
        # self.twistConnection(self.footFKJnt[0].name, self.root.tibiaRibbon.guides[-1].name )
        mc.orientConstraint(self.footFKJnt[0].name, self.root.tibiaRibbon.guides[-1].name, mo=True)
      


    def footRoll_setUp(self, footJNTList=[], parent=None):
        ''' 
            0. Creating heel jnt from the guides
                Create jnt on the plane defined by the three guides
                HeelJnt : y of toe end, z of ankle, 
                => x=?

            1. CREATING THE HIERARCHY
                footRollGRP
                    >control
                        >animParameters (footRoll, tarsalLock, strainghten)
                        >configParameters (toeRest, tarsalRest, heelLength, toeLength, tarsalLength)
                    >joints

            2. SETTING UP FOOT ROLL
                2.0. Creating Jnts
                2.1. Creating control attr
                2.2. Linking control Attr

            3. FOOT ROLL NETWORK

            4. CONNECT FOOTROLL TO LEG

            5. CONNECT FOOTROLL TO FK FOOT 
                5.0. Get Heel Toe Vector (bind pose value)
                5.1. Get Ankle Tarsal Vector 
                5.2. Angle Between vectors
                5.3. Hook Foot GRP
                5.4. Hook Toes
        '''
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()
        # 0. CREATING HEEL JNT
        # Getting the plane defined by the guides
        # Getting the 3 points
        p1 = mc.xform(footJNTList[0], ws=True, q=True, t=True)
        p2 = mc.xform(footJNTList[1], ws=True, q=True, t=True)
        p3 = mc.xform(footJNTList[2], ws=True, q=True, t=True)
        plane = fn.planeEquation(p1, p2, p3)
        # Finding x of heel jnt
        y = p3[1]; z = p1[2]
        x = -(plane[3] + plane[2]*z + plane[1]*y)/plane[0]
        heelJnt = mmod.joint(side=self.side, name=self.footName+"Heel", parent=None)
        mc.xform(heelJnt.name, ws=True, t=[x, y, z])
        # Aiming heel to toeEnd
        mc.delete(mc.aimConstraint(footJNTList[2], heelJnt, aim=[-1, 0, 0], u=[0, 1, 0], worldUpType="scene"))

        # 1. CREATING HIERARCHY
        globalFootRoll = mmod.transform(side=self.side, name=self.footName+"Roll", type="GRP", parent=parent)
        controlGrp = mmod.transform(side=self.side, name=self.footName+"Roll_controls", type="GRP", parent=globalFootRoll)
        jointsGrp =  mmod.transform(side=self.side, name=self.footName+"Roll_joints", type="GRP", parent=globalFootRoll)
        animParameters = mmod.transform(side=self.side, name=self.footName+"Roll_animParameters", type="GRP", parent=controlGrp)
        configParameters = mmod.transform(side=self.side, name=self.footName+"Roll_configParameters", type="GRP", parent=controlGrp)
        self.animParameters = animParameters
        self.configParameters = configParameters
        # 2.0. Creating Joints
        footJNTList.append(heelJnt)
        footJNTList.reverse()
        segments = self.footSegments
        segments.append("Heel")
        segments.reverse()
        newGuides = rigFn.jntHierarchy(footJNTList)
        footRolljnt = rigFn.createJntChain(newGuides, side=self.side, name=self.footName+"Roll", segmentList = segments, parent=jointsGrp)
        self.footRollJnt = footRolljnt
        mc.delete(newGuides)
        # 2.1. Creating control attr
        footRoll = animParameters.addAttr(longName="footRoll", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        tarsalLock = animParameters.addAttr(longName="tarsalLock", softMinValue=-1.7, defaultValue=0.34, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        straighten = animParameters.addAttr(longName="straighten", softMinValue=-15, defaultValue=1.5, softMaxValue=15, attrType="double", keyable=True)
        self.footRoll = footRoll
        self.tarsalLock = tarsalLock
        self.straighten = straighten
        toeRest = configParameters.addAttr( longName="toeRest", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        tarsalRest = configParameters.addAttr( longName="tarsalRest", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)

        mc.setAttr(configParameters.name+".toeRest", mc.getAttr(fn.getParent(footRolljnt[1].name)+".rotateZ"))
        mc.setAttr(configParameters.name+".tarsalRest", mc.getAttr(fn.getParent(footRolljnt[2].name)+".rotateZ"))
        # 2.2. Linking control Attr
        mmod.connectAttr(configParameters.name+".toeRest", fn.getParent(footRolljnt[1].name)+".rotateZ")
        mmod.connectAttr(configParameters.name+".tarsalRest",fn.getParent(footRolljnt[2].name)+".rotateZ")

        # 3. FOOT ROLL NETWORK
        # 3.0. HEEL BACK ROTATION
        clampHeel = mNode.clamp(side=self.side, name="footRoll"+"footRollHeel")
        mmod.connectPlugs(footRoll, clampHeel.inputR)
        mc.setAttr(clampHeel.name+".minR", -100)
        inverseMult =mNode.multDoubleLinear(side=self.side, name="footRoll"+"footRollHeel")
        mmod.connectPlugs(clampHeel.outputR, inverseMult.input1)
        mc.setAttr(inverseMult.name+".input2", -1)
        mmod.connectPlugs(inverseMult.output, footRolljnt[0].rotateZ)
        # 3.1. TARSAL ROTATION
        clampTarsalRot = mNode.clamp(side=self.side, name="footRoll"+"footRollTarsalRotation")
        clampTarsalLock = mNode.clamp(side=self.side, name="footRoll"+"footRollTarsalLock")
        mmod.connectPlugs(tarsalLock, clampTarsalLock.inputR)
        mc.setAttr(clampTarsalLock.getMaxR(), 100)
        mmod.connectPlugs(footRoll, clampTarsalRot.inputR)
        mmod.connectPlugs(clampTarsalLock.outputR, clampTarsalRot.maxR)
        # 3.2. STRAIGHTENING
        diffRollTarsalLock = mNode.plusMinusAverage(side=self.side, name="footRoll"+"toeRotation")
        clampDiff = mNode.clamp(side=self.side, name="footRoll"+"toeRotation")
        mc.setAttr(diffRollTarsalLock.getOperation(), 2)
        mmod.connectAttr(animParameters.name+".footRoll", diffRollTarsalLock.name+".input1D[0]")
        mmod.connectAttr(clampTarsalLock.getOutputR(), diffRollTarsalLock.name+".input1D[1]")
        mmod.connectAttr(diffRollTarsalLock.name+".output1D", clampDiff.getInputR())
        mc.setAttr(clampDiff.getMaxR(), 100)
        mmod.connectPlugs(clampDiff.outputR, footRolljnt[1].rotateZ)

        # Subtracting this rotation from the tarsal Rot
        invClampDiff = mNode.multDoubleLinear(side=self.side, name="footRoll"+"invToeRotation")
        straightenCoef = mNode.multDoubleLinear(side=self.side, name="footRoll"+"straightenCoef")
        addStraightening = mNode.addDoubleLinear(side=self.side, name="footRoll"+"tarsalRotation")
        mc.setAttr(invClampDiff.getInput2(), -1)
        mmod.connectPlugs(clampDiff.outputR, invClampDiff.input1)
        mmod.connectPlugs(invClampDiff.output, straightenCoef.input1)
        mmod.connectAttr(animParameters.name+".straighten", straightenCoef.getInput2())

        mmod.connectPlugs(straightenCoef.output, addStraightening.input1)
        mmod.connectAttr(clampTarsalRot.getOutputR(), addStraightening.getInput2())

        mmod.connectPlugs(addStraightening.output, footRolljnt[2].rotateZ)

        
        # 4. CONNECT FOOTROLL TO LEG
        # Get Ankle jnt WM Translation
        decompMtxFootRollAnkle = mNode.decomposeMatrix(side=self.side, name="footRoll"+"footRollAnkle")
        decompMtxAnkeCtl = mNode.decomposeMatrix(side=self.side, name="footRoll"+"ankleControl")
        subtractingTransformations = mNode.plusMinusAverage(side=self.side, name="footRoll"+"totalTransforms")
        mmod.connectAttr(footRolljnt[3].name+".worldMatrix", decompMtxFootRollAnkle.name+".inputMatrix") 
        mmod.connectAttr(self.ankleCtrl.name+".worldMatrix", decompMtxAnkeCtl.name+".inputMatrix")
        mc.disconnectAttr(self.ankleCtrl.name+".worldMatrix", decompMtxAnkeCtl.name+".inputMatrix")
        mmod.connectAttr(decompMtxFootRollAnkle.getOutputTranslate(), subtractingTransformations.name+".input3D[0]")
        mmod.connectAttr(decompMtxAnkeCtl.getOutputTranslate(), subtractingTransformations.name+".input3D[1]")
        mc.setAttr(subtractingTransformations.getOperation(), 2)
        mmod.connectAttr(subtractingTransformations.getOutput3D(), mc.listRelatives(self.ankleCtrl, c=True)[1] +".translate")


        # # 5. CONNECT FOOTROLL TO FK FOOT (WITH CONSTRAINTS)
        # 5.0. DUPLICATING FK FOOT
        localFKGrp = mmod.transform(side=self.side, name="footRoll"+"LocalFK", parent=jointsGrp)
        localFkJnt = rigFn.createJntChain(self.footJNTList, side=self.side, name="footRoll"+"LocalFK", segmentList=self.footSegments, parent=localFKGrp)
        # 5.1. ORIENT CONSTRAINT OFS GRPs
        toeOrientConstraint = mc.orientConstraint(footRolljnt[1].name, fn.getParent(localFkJnt[1].name), mo=True)[0]
        tarsalOrientConstraint = mc.orientConstraint(footRolljnt[2].name, fn.getParent(localFkJnt[0].name), mo=True)[0]
        # 5.2. SET INFLUENCES TO BE ACTIVE JUST IN IK MODE
        weight = mc.orientConstraint(toeOrientConstraint, q=True, wal=True)[0]
        mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", toeOrientConstraint+"."+weight)
        weight = mc.orientConstraint(tarsalOrientConstraint, q=True, wal=True)[0]
        mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", tarsalOrientConstraint+"."+weight)
        # 5.3. CONNECTING ROTATION TO FK OFS GRPs
        mmod.connectAttr(fn.getParent(localFkJnt[1].name)+".rotate", fn.getParent(self.footFKJnt[1].name)+".rotate")
        mmod.connectAttr(fn.getParent(localFkJnt[0].name)+".rotate", fn.getParent(self.footFKJnt[0].name)+".rotate")
        # 5.4. HIDING GRP
        mc.hide(localFKGrp)
        # 6. Connecting FootRoll to leg Ctrl
        mmod.connectPlugs(self.legRoot.footRollAttr, self.footRoll)

        # DELETING GUIDS
        mc.delete(heelJnt)


    def FKfoot_setUp(self, footJNTList=[], parent=None):
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()
        # 1. CREATING HIERARCHY
        # footConnectionFK_GRP = mmod.transform(side=self.side, name=self.footName+"FK", type="GRP", parent=parent)
        footFK_GRP = mmod.transform(side=self.side, name=self.footName+"FK", type="GRP", parent=parent)

        mc.setAttr(footFK_GRP.name+".inheritsTransform", 0)
       

        footFKJntGRP = mmod.transform(side=self.side, name=self.footName+"FK"+"Joints", type="GRP", parent=footFK_GRP)
        footConnectionFK_GRP = mmod.transform(side=self.side, name=self.footName+"FK"+"Connection", type="GRP", parent=footFKJntGRP)
        self.ikAnkleCtrlConnectionGrp= footConnectionFK_GRP


        # 2.1. CONSTRAINING FOOT TO  IK ANKLE
        decmpMatrixLimAnkle = mNode.decomposeMatrix(side=self.side, name="limitedAnkleWM")
        decmpMatrixFKAnkle = mNode.decomposeMatrix(side=self.side, name="FKAnkleWM")
        conditionNode = mNode.condition(side=self.side, name="legBlendMode")
        mmod.connectAttr(self.legRoot.limitedEffector.name+".worldMatrix", decmpMatrixLimAnkle.getInputMatrix())
        mmod.connectAttr(self.legRoot.FKjntChain[2].name+".worldMatrix", decmpMatrixFKAnkle.getInputMatrix())
        mmod.connectAttr(decmpMatrixLimAnkle.getOutputTranslate(), conditionNode.getColorIfFalse())
        mmod.connectAttr(decmpMatrixFKAnkle.getOutputTranslate(), conditionNode.getColorIfTrue())
        mmod.connectPlugs(self.legRoot.blendAttr, conditionNode.firstTerm)
        mmod.connectPlugs(conditionNode.outColor, footFKJntGRP.translate)
    
        # 2.2. FOOT JNT CHAIN
        jntChain = rigFn.createFKChain(footJNTList, side=self.side, name=self.footName+"FK", segmentList=self.footSegments, parent=footConnectionFK_GRP)
        self.footFKJnt = jntChain
        self.footFKGRP = footFKJntGRP.name

        # MATCHING GLOBAL ORIENTATION
        decomMatrix = mNode.decomposeMatrix(side=self.side, name="rootGlobalTransformations")
        mmod.connectAttr(self.hook.name+".worldMatrix", decomMatrix.getInputMatrix())
        mmod.connectAttr(decomMatrix.getOutputRotate(), footFKJntGRP.name+".rotate")
  

 




class diana(mjChr.rigSceneSetup):    
    character = "Diana"
    def __init__(self, rigName, projectEnv):
        super(diana, self).__init__(rigName, projectEnv)

        # # GLOBALS
        legMod.resetLegMod()
        armMod.resetArmMod()
        # Creating the spine
        self.m_spine = spineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self, revolveVector=[1, 0, 0])
        self.m_neck = neckMod.neck (neckJnt="C_neck00_JNT", root=self.m_spine.chestCtl, parent=self, hook=self.m_spine.cog, revolveVector=[1, 0, 0])

        side=["L", "R"]
        for s in side:
            # LEG 
            self.m_leg = legMod.leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            # self.m_leg =  leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            self.m_foot = foot(footJnt=s+"_foot00_JNT", side=s, root=self.m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)
            # ARM
            self.m_clavicle = clavicleMod.clavicle(side=s, clavicleJnt=s+"_clavicle00_JNT", root=self.m_spine.chestCtl)
            self.m_arm = armMod.arm(side=s, armJnt=s+"_arm00_JNT", parent=self, root=self.m_clavicle)
            
            # HAND
            self.m_hand =hand(handJnt=s+"_hand00_JNT", fingerGrp=s+"_handFingers00_GRP", side=s, root=self.m_arm, parent= s+"_bindArm00_GRP", hook = self.rootJnt)

       
       # CLEAN UP
        mc.select("*JNT")
        jntList = mc.ls(sl=True)
        for jnt in jntList:
            mc.setAttr(jnt+".radius", 1)


        mc.select ("*MLFT")
        matLoftList = mc.ls(sl=True)
        for node in matLoftList:
            mc.setAttr(node+".widthOffset", 1)

        # BIND JOINTS
        bindJoints = [ u'C_chest04_JNT', u'C_bindSpine013_JNT', u'C_bindSpine012_JNT', u'C_bindSpine011_JNT',
                       u'C_bindSpine010_JNT', u'C_bindSpine09_JNT', u'C_bindSpine08_JNT', u'C_bindSpine07_JNT',
                       u'C_bindSpine06_JNT', u'C_pelvis01_JNT', u'L_bindFemurribbon01_JNT', u'L_bindFemurribbon00_JNT',
                       u'L_bindFemurribbon02_JNT', u'L_bindFemurribbon03_JNT', u'L_bindFemurribbon04_JNT',
                        u'L_bindTibiaribbon00_JNT', u'L_bindTibiaribbon01_JNT', u'L_bindTibiaribbon02_JNT', u'L_bindTibiaribbon03_JNT',
                        u'L_bindTibiaribbon04_JNT', u'R_bindFemurribbon00_JNT', u'R_bindFemurribbon01_JNT',
                        u'R_bindFemurribbon02_JNT', u'R_bindFemurribbon03_JNT', u'R_bindFemurribbon04_JNT', 
                        u'R_bindTibiaribbon00_JNT', u'R_bindTibiaribbon01_JNT', u'R_bindTibiaribbon02_JNT', u'R_bindTibiaribbon03_JNT',
                        u'R_bindTibiaribbon04_JNT', u'L_footFK_Ankle00_JNT', u'R_footFK_Ankle00_JNT',
                        u'R_footFK_Tarsals01_JNT', u'L_footFK_Tarsals01_JNT', u'L_bindHumerusribbon01_JNT', u'L_bindHumerusribbon00_JNT',
                        u'L_bindHumerusribbon02_JNT', u'L_bindHumerusribbon03_JNT', u'L_bindHumerusribbon04_JNT',
                        u'L_bindRadiusribbon00_JNT', u'L_bindRadiusribbon01_JNT', u'L_bindRadiusribbon02_JNT', u'L_bindRadiusribbon03_JNT',
                        u'L_bindRadiusribbon04_JNT', u'R_bindHumerusribbon00_JNT', u'R_bindHumerusribbon01_JNT',
                        u'R_bindHumerusribbon02_JNT', u'R_bindHumerusribbon03_JNT', u'R_bindHumerusribbon04_JNT',
                        u'R_bindRadiusribbon00_JNT', u'R_bindRadiusribbon01_JNT', u'R_bindRadiusribbon02_JNT', u'R_bindRadiusribbon03_JNT',
                        u'R_bindRadiusribbon04_JNT',
                        u'L_bindClavicle012_JNT', u'R_bindClavicle012_JNT', 
                        u'L_handFK_wrist00_JNT', u'R_handFK_wrist00_JNT', 
                        u'L_thumbMetacarpal00_JNT', u'L_thumbProximalPhalange02_JNT', u'L_thumbMiddlePhalange04_JNT',
                        u'R_thumbMetacarpal00_JNT', u'R_thumbProximalPhalange02_JNT', u'R_thumbMiddlePhalange04_JNT',
                        u'L_indexMetacarpal00_JNT', u'L_indexProximalPhalange02_JNT', u'L_indexMiddlePhalange04_JNT', 
                        u'L_indexDistalPhalange06_JNT', u'L_middleMetacarpal00_JNT', u'L_middleProximalPhalange02_JNT', 
                        u'L_middleMiddlePhalange04_JNT', u'L_middleDistalPhalange06_JNT', u'L_ringMetacarpal00_JNT', 
                        u'L_ringProximalPhalange02_JNT', u'L_ringMiddlePhalange04_JNT', u'L_ringDistalPhalange06_JNT',
                        u'L_pinkyMetacarpal01_JNT', u'L_pinkyProximalPhalange03_JNT', u'L_pinkyMiddlePhalange05_JNT',
                        u'L_pinkyDistalPhalange07_JNT', u'R_indexMetacarpal00_JNT', u'R_indexProximalPhalange02_JNT',
                        u'R_indexMiddlePhalange04_JNT', u'R_indexDistalPhalange06_JNT', u'R_middleMetacarpal00_JNT',
                        u'R_middleProximalPhalange02_JNT', u'R_middleMiddlePhalange04_JNT', u'R_ringMetacarpal00_JNT', 
                        u'R_pinkyMetacarpal01_JNT', u'R_pinkyProximalPhalange03_JNT', u'R_ringProximalPhalange02_JNT', 
                        u'R_pinkyMiddlePhalange05_JNT', u'R_ringMiddlePhalange04_JNT', u'R_pinkyDistalPhalange07_JNT',
                        u'R_ringDistalPhalange06_JNT', u'R_middleDistalPhalange06_JNT', 
                        u'L_thumbMetacarpal01_JNT', u'L_thumbProximalPhalange03_JNT', u'L_indexMetacarpal01_JNT', 
                        u'L_indexProximalPhalange03_JNT', u'L_indexMiddlePhalange05_JNT', u'L_middleMetacarpal01_JNT',
                        u'L_middleProximalPhalange03_JNT', u'L_middleMiddlePhalange05_JNT', u'L_ringMetacarpal01_JNT', 
                        u'L_ringProximalPhalange03_JNT', u'L_ringMiddlePhalange05_JNT', u'L_pinkyMetacarpal02_JNT', 
                        u'L_pinkyProximalPhalange04_JNT', u'L_pinkyMiddlePhalange06_JNT', 
                        u'R_thumbMetacarpal01_JNT', u'R_thumbProximalPhalange03_JNT', u'R_indexMetacarpal01_JNT', 
                        u'R_indexProximalPhalange03_JNT', u'R_indexMiddlePhalange05_JNT', u'R_middleMetacarpal01_JNT',
                        u'R_middleProximalPhalange03_JNT', u'R_middleMiddlePhalange05_JNT', u'R_ringMetacarpal01_JNT', 
                        u'R_ringProximalPhalange03_JNT', u'R_ringMiddlePhalange05_JNT', u'R_pinkyMetacarpal02_JNT', 
                        u'R_pinkyProximalPhalange04_JNT', u'R_pinkyMiddlePhalange06_JNT', 
                        u'C_bindNeck03_JNT', u'C_bindNeck04_JNT', u'C_bindNeck05_JNT', 
                        u'C_bindNeck06_JNT', u'C_bindNeck07_JNT', u'C_bindNeck08_JNT', u'C_head00_JNT']

    #     # # POSITIONING JOINTS AT RIGHT PLACES
    #     # # SPINE
        
    #     # TEMPORARY
        # mc.hide("C_geometry01_GRP")
        mc.hide ("Groom", "Light", "Eye1")
        mc.select("C_spineFKCtl0*_JNT")
        mc.delete()

        
        mc.select(bindJoints, "Diana_Geo")



rig=diana("Diana", projectEnv)
