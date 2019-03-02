
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




class finger(object):
    globalCtrl=None
    def __init__(self, jntHierarchy, fingerName="finger", side="C", parent=None, hook=None, worldUpVector=""):
        '''
        NAMES
        fingerName ={thumb, index, middle, ring, pinky}


        1. HIERARCHY STRUCTURE
            fingerName_GRP
                metacarpal_GRP>OFS>JNT
                    phalangeA00_GRP>OFS>CTL>JNT
                        phalangeB00_GRP>OFS>CTL>JNT
                            phalangeC00_GRP>OFS>CTL>JNT
                         
        '''

        # GLOBALS
        self.side = side
        self.parent = parent
        self.hook = hook
        self.worldUpVector = worldUpVector
        mmod.resetCount()

        metacarpalName = fingerName+"Metacarpal"
        phalangeName = [fingerName+"ProximalPhalange", fingerName+"MiddlePhalange", fingerName+"DistalPhalange"] 
        guidJntList = mc.listRelatives(jntHierarchy, ad=True); guidJntList.reverse()
        fingerBaseJnt=[]

        aimVector = [1, 0, 0]
        upVector = [0, 1, 0]
                

        # CREATING HIERARCHY
        self.fingerGRP = mmod.transform(side=side, name=fingerName, type="GRP", parent=parent)
        # worldUpVector
        
        # GLOBAL CTRL
        if (fingerName=="pinky"):
            finger.globalCtrl = rigFn.constructCTL(jntHierarchy, side=side, name=metacarpalName, parent=self.fingerGRP)
            #metaJntA = fn.getChildren(self.globalCtrl.name)[1]
            #fingerBaseJnt.append(metaJntA)

        metaJntA = rigFn.constructJNT(jntHierarchy, side=side, name=metacarpalName, parent=self.fingerGRP)
        fingerBaseJnt.append(metaJntA.name)

        # METACARPAL JNT        
        metaJntB = mmod.joint(side=side, name=metacarpalName, parent=metaJntA)
        metaJntB.translateX=mc.xform(guidJntList[0], q=True, r=True, t=True)[0]
        metaGrp = mmod.transform(side=side, name=metacarpalName, parent=fn.getParent(metaJntA), type="GRP")
        mc.parent(metaJntA, metaGrp)
        
        # PHALANGES JNT
        for i, jnt in enumerate(guidJntList[:-1]):
            phalangeCTL = rigFn.constructCTL(jnt, side=side, name=phalangeName[i], parent=fn.getParent(metaJntA) if i==0 else phalangeCTL)
            fingerBaseJnt.append(mc.listRelatives(phalangeCTL, c=True, typ="joint")[0])
            jntB = mmod.joint(side=side, name=phalangeName[i], parent=fingerBaseJnt[i+1])

            # AIM CONSTRAINTS
            # Creating WorldUpObject
            worldUpObj = mmod.transform(side=self.side, name=fingerName+str(i)+"WorldUpObject", parent=fn.getParent(fingerBaseJnt[i]))
            fn.snapTool(fingerBaseJnt[i], worldUpObj)
            mc.aimConstraint(fingerBaseJnt[i+1], fingerBaseJnt[i], aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=worldUpObj)

            
            # JOINT STRETCHING
            distanceBetweenNode = mc.createNode("distanceBetween", name=side+"_distance"+fingerName+str(i)+"_DST")
            #print fingerBaseJnt[i], "jnt"
            mc.connectAttr(fingerBaseJnt[i]+".worldMatrix", distanceBetweenNode+".inMatrix1")
            mc.connectAttr(fingerBaseJnt[i+1]+".worldMatrix", distanceBetweenNode+".inMatrix2")

            # Minus operation
            minusNode = mc.createNode("plusMinusAverage", name=side+"_subtract"+fingerName+str(i)+"_PMA")
            mc.setAttr(minusNode+".operation", 2)
            mc.connectAttr(distanceBetweenNode+".distance", minusNode+".input1D[0]")
            mc.connectAttr(fingerBaseJnt[i+1]+".radius", minusNode+".input1D[1]")
            # Scalingby global scale
            divide = mNode.multiplyDivide(side=self.side, name=fingerName+str(i)+"GlobalScale")
            worldTransformation = mNode.decomposeMatrix(side=self.side, name = "rootGlobalTransformation")
            mmod.connectAttr(self.hook.name+".worldMatrix", worldTransformation.getInputMatrix())
            mmod.connectAttr(minusNode+".output1D", divide.name+".input1X")
            divide.operation = 2
            mmod.connectAttr(worldTransformation.getOutputScale(), divide.getInput2())
            mc.connectAttr(divide.name+".outputX", fn.getChildren(fingerBaseJnt[i])[0]+".translateX")

            # POSITIONING END JNT
            if (jnt==guidJntList[-2]):
                translateX = mc.getAttr(guidJntList[-1]+".translateX")
                mc.setAttr(fn.getChildren(fingerBaseJnt[-1])[0]+".translateX", translateX)


        self.fingerJntChain = fingerBaseJnt

        # DELETING GUIDES
        mc.delete(jntHierarchy)

class hand():

    def __init__(self, handJnt=None, fingerGrp=None, side="C", name="hand", parent=None, root=None, hook=None):
        '''
        Hand Module
        parent = object to parent too
        root = arm 
        hook = rootJnt for global scale

        Creating a finger obj for each of the jnt Chain in the hierarchy 
        '''
        # SELF
        self.side = side
        self.name = name
        self.handJnt = hand
        self.fingerGrp = fingerGrp
        self.parent = parent
        self.root = root
        self.hook = hook
        self.guideHandJnt = handJnt

        # GLOBALS
        mmod.resetCount()


        # CREATING HIERARCHY
        handGrp = mmod.transform(side=self.side, name="hand", type="GRP", parent=self.parent)
        self.handGrp = handGrp

        # CONNECTING HAND GROUP TO WRIST MOVEMENT
        self.connectToWristMovement()

        handFingersGRP = mmod.transform(side=self.side, name="handFingers", type="GRP", parent=handGrp)
        self.handFingersGRP = handFingersGRP
        # Creating Hand Jnt
        mc.parent(self.guideHandJnt, self.handGrp)
        # CREATING FINGERS
        fingerJntList = fn.getChildren(fingerGrp)
        print "finger grp", fingerGrp
        print fingerJntList
        fingers=[]
        for jnt in fingerJntList:
            name = fn.concat_str(jnt, s1_begin = 2, s1_end=6)
            fingerObj = finger(jnt, fingerName=name, side=self.side, parent=handFingersGRP, hook=self.hook)
            fingers.append(fingerObj)

        # CREATE GLOBAL ROTATE
        for i, f in enumerate(fingers):
            '''if (i==0):
                mmod.connectAttr(finger.globalCtrl.name+'.rotateZ', fn.getParent(f.fingerJntChain[0])+'.rotateZ')
            else:'''
        
            # CREATING SCALING FACTOR
            multNode = mNode.multDoubleLinear(side=self.side, name="globalRotateScalingFactor")
            mmod.connectAttr(finger.globalCtrl.name+'.rotateZ', multNode.getInput1())
            mc.setAttr(multNode.getInput2(), (i*20)/100.0+0.05)
            mmod.connectAttr(multNode.getOutput(), fn.getParent(f.fingerJntChain[0])+'.rotateZ')
        
        # MATCHING GLOBAL ORIENTATION
        decomMatrix = mNode.decomposeMatrix(side=self.side, name="rootGlobalTransformations")
        mmod.connectAttr(self.hook.name+".worldMatrix", decomMatrix.getInputMatrix())
        mmod.connectAttr(decomMatrix.getOutputRotate(),  self.handFingersGRP.name+".rotate")

       
        # DELETING GUIDES
        mc.delete(fingerGrp)
    def connectToWristMovement(self):
        # CONNECTING TRANSLATION
        # Getting Local Space
        mc.setAttr(self.handGrp.name+".inheritsTransform" , 0)
        # matrixMult = mNode.multMatrix(side=self.side, name=self.name+"LocalSpace")
        decopMatrix = mNode.decomposeMatrix(side=self.side, name=self.name+"LocalSpace")
        # mmod.connectAttr(self.root.bindJntChain[-1].name+".worldMatrix", matrixMult.name+".matrixIn[0]")
        # mmod.connectAttr(self.parent+".worldInverseMatrix", matrixMult.name+".matrixIn[1]")
        # mmod.connectPlugs(matrixMult.matrixSum, decopMatrix.inputMatrix)
        mmod.connectAttr(self.root.bindJntChain[-1].name+".worldMatrix", decopMatrix.getInputMatrix())
        mmod.connectPlugs(decopMatrix.outputTranslate, self.handGrp.translate)
        # CONNECTING ROTATION
        # additive = mNode.animBlendNodeAdditiveDA(side=self.side, name=self.name+"ReverseRotationX")
        # mmod.connectAttr(self.root.effectorCtrl.name+".rotateX", additive.getInputA())
        # additive.weightA = -1
        # mmod.connectAttr(additive.getOutput(), self.handGrp.name+".rotateZ")
        mmod.connectAttr(self.root.effectorCtrl.name+".rotateX", self.handGrp.name+".rotateX")
        mmod.connectAttr(self.root.effectorCtrl.name+".rotateY", self.handGrp.name+".rotateY")
        mmod.connectAttr(self.root.effectorCtrl.name+".rotateZ", self.handGrp.name+".rotateZ")

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
            print self.m_clavicle.clavicleControl[1]
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
                        u'L_bindTibiaribbon00_JNT',
                        u'L_bindTibiaribbon01_JNT',
                        u'L_bindTibiaribbon02_JNT',
                        u'L_bindTibiaribbon03_JNT',
                        u'L_bindTibiaribbon04_JNT',
                        u'L_bindTibiaribbon05_JNT',
                        u'R_bindFemurribbon00_JNT',
                        u'R_bindFemurribbon01_JNT',
                        u'R_bindFemurribbon02_JNT',
                        u'R_bindFemurribbon03_JNT',
                        u'R_bindFemurribbon04_JNT',
                        u'R_bindFemurribbon05_JNT',
                        u'R_bindTibiaribbon00_JNT',
                        u'R_bindTibiaribbon01_JNT',
                        u'R_bindTibiaribbon02_JNT',
                        u'R_bindTibiaribbon03_JNT',
                        u'R_bindTibiaribbon04_JNT',
                        u'R_bindTibiaribbon05_JNT',
                        u'L_footFK_Ankle00_JNT',
                        u'R_footFK_Ankle00_JNT',
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
        mc.hide ("Groom")
        mc.select("C_spineFKCtl0*_JNT")
        mc.delete()

        
        mc.select(bindJoints, "Diana_Geo")



rig=diana("Diana", projectEnv)
