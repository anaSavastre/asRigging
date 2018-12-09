''' 
Ana Maria Savastre
Bournemouth University 

Master Class Assignment: Frontier Rigging 

Character: Spinosaurus


'''
import maya.cmds as mc
import loadFn 


# TEMP
import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 


# Body Modules
import spineModule as spineMod
import armModule as armMod
import scapulaModule as scapulaMod
import legModule as legMod
import footModule as footMod
import tailModule as tailMod
# GLOBALS
projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"

 

class spinosaurus(loadFn.rigSceneSetup):
    character = "spinosaurus"
    def __init__(self, rigName, projectEnv):
        super(spinosaurus, self).__init__(rigName, projectEnv)

        # GLOBALS
        legMod.resetLegMod()
        armMod.resetArmMod()
        scapulaMod.resetScapulaMod()
        tailMod.resetTailMod()


        # Creating the spine
        m_spine = spineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self)
        # Creating the neck
        # my_neck = spine(spineJnt="C_neck00_JNT", root=my_spine.chestCtl, parent=self)

        # Creating the tail
        m_tail = tailMod.tail(tailJnt="C_tail00_JNT", numbControlPoints=4, parent=self, root=m_spine.pelvisCtl)
        # Creating the arms, scapula, legs, foot
        side =["L", "R"]
        for s in side:

            m_arm =armMod.arm(side=s, armJnt=s+"_armShoulder00_JNT", parent=self, root=m_spine.chestCtl)
            m_scapula =scapulaMod.scapula(side=s, scapulaJnt=s+"_scapula00_JNT", parent = self, root=m_spine.chestCtl, armJnt=m_arm)
            m_leg =legMod.leg(legJnt=s+"_legHip00_JNT", side=s, parent=self, root=m_spine.pelvisCtl)
            m_foot = footMod.foot(footJnt=s+"_footAnkle00_JNT", side=s, root=m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)

        # TEMPORARY
        mc.hide("C_geometry01_GRP")



rig=spinosaurus("Spinosaurus", projectEnv)
