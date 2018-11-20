''' 
Ana Maria Savastre
Bournemouth University 

Master Class Assignment: Frontier Rigging 

Character: Spinosaurus


'''

import maya.cmds as mc

import shutil 
import os 
import sys
import mayaModule as mmod
import functions as fn
import loadFn 
import legModule as legMod

# GLOBALS
projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"
        

class spinosaurus(loadFn.rigSceneSetup):
    character = "lsla"
    def __init__(self, rigName, projectEnv):
        super(spinosaurus, self).__init__(rigName, projectEnv)

        # Creating the legs
        side =["L", "R"]
        for s in side:
            leg = legMod.leg(legJnt=s+"_legHip00_JNT", ankleGuide=s+"_legAnkleGuid00_LOC", side=s)
            foot = legMod.foot(footJnt=s+"_footAnkle00_JNT", side=s, root=leg, parent=s+"_legBind00_GRP")


        # R_leg = leg(legJnt="R_legHip00_JNT", ankleGuide="R_legAnkleGuid00_LOC", side="R")
        # R_foot = foot(footJnt="R_footAnkle00_JNT", side="R", root=R_leg, parent="R_legBind00_GRP")





rig=spinosaurus("Spinosaurus", projectEnv)
