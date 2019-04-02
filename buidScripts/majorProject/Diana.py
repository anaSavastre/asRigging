
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



class leg(blendFKIK.blendFKIK):
    rigParent = None
  
    def volumePreservationSetUp(self, ribbonLimb, ribbonName=""):            
        # MultiplyDivide NODE
        multiplyDiv = mNode.multiplyDivide(side=self.side, name=self.name+"DivLen")
        mc.setAttr(multiplyDiv.name+".input1X", mc.getAttr(ribbonLimb.ribbon.matloftNode.getSurfaceLength()) )
        multiplyDiv.operation = 2
        mmod.connectAttr(ribbonLimb.ribbon.matloftNode.getSurfaceLength(), multiplyDiv.name+".input2X")

        # Volume Preservation Condition
        condNode = mNode.condition(side=self.side, name=self.name+"VolumePreservationCond")
        condNode.secondTerm = 1
        # mmod.connectAttr(multiplyDiv.name+".outputX", condNode.getFirstTerm())
        mmod.connectAttr(multiplyDiv.getOutput(), condNode.getColorIfTrue())
        mmod.connectAttr(self.settingCtl.name+".volumePreservation", condNode.getFirstTerm())

        # Power Nodes
        for i in range (len(ribbonLimb.ribbon.ribbonJoints)):
            attrName = ribbonName+"RibbonMagnitude"+str(i)
            magnitudeAttr =mc.addAttr(self.settingCtl.name, longName=attrName, min=-2, dv=0, max=2, at="double", keyable=True)
            powerNode = mNode.multiplyDivide(side=self.side, name=self.name+ribbonName.capitalize()+"PowerNode")
            mmod.connectAttr(condNode.name+".outColorR", powerNode.name+".input1X")
            mmod.connectAttr(self.settingCtl.name+"."+attrName, powerNode.name+".input2X")
            powerNode.operation = 3
            # Connecting To JNT Scale
            mmod.connectAttr(powerNode.name+".outputX",  ribbonLimb.ribbon.ribbonJoints[i].name+".scaleY")
            mmod.connectAttr(powerNode.name+".outputX",  ribbonLimb.ribbon.ribbonJoints[i].name+".scaleZ")

    def __init__(self, side="C", legJnt=None, parent=None, root=None):
        if (parent!=None):
            if(leg.rigParent==None):
                leg.rigParent=mmod.transform(name="legGlobal", type="GRP", parent=parent.rigGrp)
        super(leg, self).__init__(side=side, jnt=legJnt, name="leg", segmentsList=["Hip", "Knee", "Ankle"], parent=leg.rigParent, root=root,  hook=parent.rootJnt)
        
        # FootRoll Attribute
        self.footRollAttr = self.effectorCtrl.addAttr(longName="footRoll", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        # RIBBON LIMBS
        # RIBBON VISIBILITY SWITCH ATTR
        ribbonVisibility = self.settingCtl.addAttr(longName = "secondaryControls", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)


        # CREATING MAGNITUDE ATTR
        # Volume Preservation Attr
        volumePreservation =mc.addAttr(self.settingCtl.name, longName="volumePreservation", min=0, dv=1, max=1, at="short", keyable=True)

        self.legRibbonGrp = mmod.transform(side=self.side, name="ribbonLeg", type="GRP", parent = leg.rigParent)

        self.femurRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "femurRibbon", parent=leg.rigParent, root=fn.getChildren(root)[1], revolveVector=[0, 0, 1])
        self.tibiaRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "tibiaRibbon", parent=leg.rigParent, root=fn.getChildren(root)[1], revolveVector=[0, 0, 1])
        

        # CONSTRAINING FEMUR UPPER CTRL TO PELVIS
        rigFn.parentConstraintMO (self.root.name, fn.getParent(fn.getParent(self.femurRibbon.guides[0])), fn.getParent(self.femurRibbon.guides[0]), translate=False, rotate=True, scale=False )
        # AIM FEMUR START TO KNEE
        aimGroup = mmod.transform(side=self.side, name="femurRibbonAim", type="GRP", parent = fn.getParent(self.femurRibbon.guides[0]))
        mc.parent(self.femurRibbon.guides[0], aimGroup)
        mc.aimConstraint(self.tibiaRibbon.ribbon.ribbonJoints[0],  aimGroup, aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root, mo=True)
        # KNEE CONTROL
        rigFn.parentConstraintMO(self.tibiaRibbon.guides[0].name, fn.getParent(self.femurRibbon.guides[-1]), self.femurRibbon.guides[-1].name, maintainOffset = True, translate=True, rotate=True, scale=False)
        # RIBBON GLOBAL
        self.ribbonGlobalCtrl()
        
        # CREATING VOLUME PRESERVATION
        self.volumePreservationSetUp(self.femurRibbon, ribbonName="femur")
        self.volumePreservationSetUp(self.tibiaRibbon, ribbonName="tibia")

        # RIBBON VISIBILITY SWITCH
        mc.hide(self.femurRibbon.guides[0], self.femurRibbon.guides[-1], self.tibiaRibbon.guides[0], self.tibiaRibbon.guides[-1])
        for femurControl, tibiaControl  in zip(self.femurRibbon.guides[1:-1], self.tibiaRibbon.guides[1:-1]):
            mmod.connectPlugs(ribbonVisibility, femurControl.visibility)
            mmod.connectPlugs(ribbonVisibility, tibiaControl.visibility)
        mmod.connectPlugs(ribbonVisibility, self.tibiaRibbon.guides[0].visibility)
        mmod.connectPlugs(ribbonVisibility, self.globalRibbonCtrl.visibility)


    def ribbonGlobalCtrl (self):
        # Creating Control
        self.globalRibbonCtrl = rigFn.constructCTL(fn.getChildren(self.tibiaRibbon.guides[0].name)[1], side=self.side, name="legRibbonGlobal", parent=self.legRibbonGrp, ctrlScale=1, ctrlShape=0)
        fn.scaleShapePoints(fn.getChildren(self.globalRibbonCtrl)[0], 10)
        # Connecting Control To Ribbon System
        # Elbow Ctrl
        guide = self.tibiaRibbon.guides[0]
        connectionsGrp = mmod.transform(side=self.side, name="legGlobalConnection", type="GRP", parent = fn.getParent(guide))
        mc.parent(guide, connectionsGrp)
        mmod.connectAttr(self.globalRibbonCtrl.name+".translate", connectionsGrp.name+".translate")
        # 1. Creating Connection Grps
        # Hummerus Guide
        connectionsGrpFemur = mmod.transform(side=self.side, name="legGlobalConnection", type="GRP", parent = fn.getParent(self.femurRibbon.guides[2]))
        mc.parent(self.femurRibbon.guides[2], connectionsGrpFemur)
        # Tibia Guide
        connectionsGrpTibia = mmod.transform(side=self.side, name="legGlobalConnection", type="GRP", parent = fn.getParent(self.tibiaRibbon.guides[2]))
        mc.parent(self.tibiaRibbon.guides[2], connectionsGrpTibia)
        # 2. Creating Weight Attr
        globalCtlWeight = self.settingCtl.addAttr(longName = "ribbonGlobWeight", softMinValue=-1, defaultValue=0.25, softMaxValue=1, attrType="double", keyable=True)
        # 3. Multiply divide node
        multiplyDivideNode = mNode.multiplyDivide(side=self.side, name=self.name+"ribbonGlobalCtrlWeigth")
        # 4. Connections
        mmod.connectAttr(self.globalRibbonCtrl.name+".translate", multiplyDivideNode.getInput1())
        mmod.connectAttr(self.settingCtl.name+".ribbonGlobWeight", multiplyDivideNode.name+".input2X")
        mmod.connectAttr(self.settingCtl.name+".ribbonGlobWeight", multiplyDivideNode.name+".input2Y")
        mmod.connectAttr(self.settingCtl.name+".ribbonGlobWeight", multiplyDivideNode.name+".input2Z")
        mmod.connectAttr(multiplyDivideNode.getOutput(), connectionsGrpFemur.name+".translate")
        mmod.connectAttr(multiplyDivideNode.getOutput(), connectionsGrpTibia.name+".translate")        

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
            self.m_leg = leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            # self.m_leg =  leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            self.m_foot = footMod.foot(footJnt=s+"_foot00_JNT", side=s, root=self.m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)
            # ARM
            self.m_clavicle = clavicleMod.clavicle(side=s, clavicleJnt=s+"_clavicle00_JNT", root=self.m_spine.chestCtl)
            self.m_arm = armMod.arm(side=s, armJnt=s+"_arm00_JNT", parent=self, root=self.m_clavicle)
            
            # HAND
            self.m_hand =handMod.hand(handJnt=s+"_hand00_JNT", fingerGrp=s+"_handFingers00_GRP", side=s, root=self.m_arm, parent= s+"_bindArm00_GRP", hook = self.rootJnt)

       
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
        bindJoints = [ u'C_chest04_JNT', u'C_bindSpine06_JNT', u'C_bindSpine010_JNT', u'C_bindSpine09_JNT', u'C_bindSpine08_JNT', u'C_bindSpine07_JNT',
                       u'C_pelvis01_JNT', u'L_bindFemurribbon01_JNT', u'L_bindFemurribbon00_JNT',
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
                        u'R_bindRadiusribbon04_JNT', u'L_bindClavicle012_JNT', u'R_bindClavicle012_JNT', 
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
                        u'C_bindNeck02_JNT', u'C_bindNeck03_JNT', u'C_bindNeck04_JNT', 
                        u'C_bindNeck06_JNT', u'C_bindNeck05_JNT', u'C_head00_JNT']

    #     # # POSITIONING JOINTS AT RIGHT PLACES
    #     # # SPINE
        
    #     # TEMPORARY
        # mc.hide("C_geometry01_GRP", "Dress")
        mc.hide ("Groom")#, "Light", "Eye1")
        mc.select("C_spineFKCtl0*_JNT")
        mc.delete()

        
        mc.select(bindJoints, "C_Diana00_GEO")



rig=diana("Diana", projectEnv)



# # CLEAM UP
# def cleanUp():
        
#     mc.select("*_JNT")

#     list = mc.ls(sl=True)

#     for jnt in list:
#         mc.setAttr(jnt+".drawStyle", 2)


# cleanUp()