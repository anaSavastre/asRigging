
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

 
class diana(mjChr.rigSceneSetup):    
    character = "Diana"
    def __init__(self, rigName, projectEnv):
        super(diana, self).__init__(rigName, projectEnv)

        # # GLOBALS
        legMod.resetLegMod()
        armMod.resetArmMod()
        # Creating the spine
        self.m_spine =  spineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self, revolveVector=[1, 0, 0])
        self.m_neck = neckMod.neck (neckJnt="C_neck00_JNT", root=self.m_spine.chestCtl, parent=self, hook=self.rootJnt, revolveVector=[1, 0, 0])

        side=["L", "R"]
        for s in side:
            # LEG 
            self.m_leg =  legMod.leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
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
                        u'C_bindNeck03_JNT', u'C_bindNeck04_JNT', u'C_bindNeck07_JNT',
                        u'C_bindNeck06_JNT', u'C_bindNeck05_JNT', u'C_head00_JNT']

        # POSITIONING JOINTS AT RIGHT PLACES
        # SPINE
        
        # TEMPORARY
        # mc.hide("C_geometry01_GRP", "C_Dress00_GEO")
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