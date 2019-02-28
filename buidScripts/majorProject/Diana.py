
''' 
Ana Maria Savastre
Bournemouth University 

Major Project: Richest Girl in Town

Character: Diana


'''

import maya.cmds as mc
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

class diana(loadFn.rigSceneSetup):    
    character = "Diana"
    def __init__(self, rigName, projectEnv):
        super(diana, self).__init__(rigName, projectEnv)

        # GLOBALS
        legMod.resetLegMod()
        armMod.resetArmMod()
        # Creating the spine
        self.m_spine = spineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self, revolveVector=[0, 0, 1])
        self.m_neck = neckMod.neck (neckJnt="C_neck00_JNT", root=self.m_spine.chestCtl, parent=self, hook=self.m_spine.cog, revolveVector=[1, 0, 0])
        

        side=["L", "R"]
        for s in side:
            # LEG 
            self.m_leg = legMod.leg(legJnt=s+"_leg00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            self.m_foot = foot(footJnt=s+"_foot00_JNT", side=s, root=self.m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)
            # ARM
            self.m_clavicle = clavicleMod.clavicle(side=s, clavicleJnt=s+"_clavicle00_JNT", root=self.m_spine.chestCtl)
            print self.m_clavicle.clavicleControl[1]
            self.m_arm = armMod.arm(side=s, armJnt=s+"_arm00_JNT", parent=self, root=self.m_clavicle.clavicleControl[1])
        # CLEAN UP
        mc.select("*JNT")
        jntList = mc.ls(sl=True)
        for jnt in jntList:
            mc.setAttr(jnt+".radius", 1)

        mc.select ("*MLFT")
        matLoftList = mc.ls(sl=True)
        for node in matLoftList:
            mc.setAttr(node+".widthOffset", 1)

        # POSITIONING JOINTS AT RIGHT PLACES
        # SPINE
        
        # TEMPORARY
        mc.hide("C_geometry01_GRP")
        mc.select("C_spineFKCtl0*_JNT")
        mc.delete()



rig=diana("Diana", projectEnv)
