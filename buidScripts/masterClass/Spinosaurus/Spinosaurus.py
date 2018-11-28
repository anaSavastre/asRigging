''' 
Ana Maria Savastre
Bournemouth University 

Master Class Assignment: Frontier Rigging 

Character: Spinosaurus


'''

import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import loadFn 
import asNodes as asNode
import math as math

import legModule as legMod
import spineModule as sineMod

# GLOBALS
projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"

def deistBetween(point1, point2):
    dist = math.sqrt((point2[0] - point1[0])*(point2[0] - point1[0]) + (point2[1] - point1[1])*(point2[1] - point1[1]) + (point2[2] - point1[2])*(point2[2] - point1[2]))
    return dist
         

        
class spinosaurus(loadFn.rigSceneSetup):
    character = "spinosaurus"
    def __init__(self, rigName, projectEnv):
        super(spinosaurus, self).__init__(rigName, projectEnv)

        # Creating the spine
        my_spine = sineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self)
        # Creating the neck
        # my_neck = spine(spineJnt="C_neck00_JNT", root=my_spine.chestCtl, parent=self)

        # Creating the legs
        side =["L", "R"]
        for s in side:
            leg = legMod.leg(legJnt=s+"_legHip00_JNT", ankleGuide=s+"_legAnkleGuid00_LOC", side=s)
            foot = legMod.foot(footJnt=s+"_footAnkle00_JNT", side=s, root=leg, parent=s+"_legBind00_GRP")


        # TEMPORARY
        # mc.hide("C_geometry01_GRP")



rig=spinosaurus("Spinosaurus", projectEnv)
