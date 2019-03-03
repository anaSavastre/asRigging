
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
import ribbonLimbs as ribbonLimbs

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

class diana(mjChr.rigSceneSetup):    
    character = "Diana"
    def __init__(self, rigName, projectEnv):
        super(diana, self).__init__(rigName, projectEnv)

        # # GLOBALS
        legMod.resetLegMod()
        armMod.resetArmMod()
        # Creating the spine
        self.m_spine = spineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self, revolveVector=[0, 0, 1])
        self.m_neck = neckMod.neck (neckJnt="C_neck00_JNT", root=self.m_spine.chestCtl, parent=self, hook=self.m_spine.cog, revolveVector=[1, 0, 0])

        side=["L", "R"]
        for s in side:
            # LEG 
            self.m_leg = legMod.leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            self.m_foot = footMod.foot(footJnt=s+"_foot00_JNT", side=s, root=self.m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)
            # ARM
            self.m_clavicle = clavicleMod.clavicle(side=s, clavicleJnt=s+"_clavicle00_JNT", root=self.m_spine.chestCtl)
            self.m_arm = armMod.arm(side=s, armJnt=s+"_arm00_JNT", parent=self, root=self.m_clavicle.clavicleControl[1])
              
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
                       u'L_bindFemurribbon02_JNT', u'L_bindFemurribbon03_JNT', u'L_bindFemurribbon04_JNT', u'L_bindFemurribbon05_JNT',
                        u'L_bindTibiaribbon00_JNT', u'L_bindTibiaribbon01_JNT', u'L_bindTibiaribbon02_JNT', u'L_bindTibiaribbon03_JNT',
                        u'L_bindTibiaribbon04_JNT', u'L_bindTibiaribbon05_JNT', u'R_bindFemurribbon00_JNT', u'R_bindFemurribbon01_JNT',
                        u'R_bindFemurribbon02_JNT', u'R_bindFemurribbon03_JNT', u'R_bindFemurribbon04_JNT', u'R_bindFemurribbon05_JNT',
                        u'R_bindTibiaribbon00_JNT', u'R_bindTibiaribbon01_JNT',
                        u'R_bindTibiaribbon02_JNT', u'R_bindTibiaribbon03_JNT',
                        u'R_bindTibiaribbon04_JNT', u'R_bindTibiaribbon05_JNT',
                        u'L_footFK_Ankle00_JNT', u'R_footFK_Ankle00_JNT',
                        u'R_footFK_Tarsals01_JNT',
                        u'L_footFK_Tarsals01_JNT',
                        u'L_bindHumerusribbon01_JNT',
                        u'L_bindHumerusribbon00_JNT',
                        u'L_bindHumerusribbon02_JNT',
                        u'L_bindHumerusribbon03_JNT',
                        u'L_bindHumerusribbon04_JNT',
                        u'L_bindHumerusribbon05_JNT',
                        u'L_bindRadiusribbon00_JNT',
                        u'L_bindRadiusribbon01_JNT',
                        u'L_bindRadiusribbon02_JNT',
                        u'L_bindRadiusribbon03_JNT',
                        u'L_bindRadiusribbon04_JNT',
                        u'L_bindRadiusribbon05_JNT',
                        u'R_bindHumerusribbon00_JNT',
                        u'R_bindHumerusribbon01_JNT',
                        u'R_bindHumerusribbon02_JNT',
                        u'R_bindHumerusribbon03_JNT',
                        u'R_bindHumerusribbon04_JNT',
                        u'R_bindHumerusribbon05_JNT',
                        u'R_bindRadiusribbon00_JNT',
                        u'R_bindRadiusribbon01_JNT',
                        u'R_bindRadiusribbon02_JNT',
                        u'R_bindRadiusribbon03_JNT',
                        u'R_bindRadiusribbon04_JNT',
                        u'R_bindRadiusribbon05_JNT']



        # # POSITIONING JOINTS AT RIGHT PLACES
        # # SPINE
        
        # TEMPORARY
        mc.hide("C_geometry01_GRP")
        mc.hide ("Groom", "Light", "Eye:group1")
        mc.select("C_spineFKCtl0*_JNT")
        mc.delete()

        
        mc.select(bindJoints, "Diana_Geo")



rig=diana("Diana", projectEnv)
