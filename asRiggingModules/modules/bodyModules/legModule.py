''' 
            Leg module
                        Ana Maria Savastre
                        Bournemouth University 

Module that creates the leg

GUIDE REQUIREMENTS

IMPLEMENTATION:
    1. Limited foot (foot doesn't go bewond the max distance of the jnt chain)

'''



import maya.cmds as mc
import mayaModule as mmod
import blendFKIK as blendFKIK
import ribbonLimbs as ribbonLimbs
import functions as fn



def resetLegMod():
    leg.rigParent = None
    
class leg(blendFKIK.blendFKIK):
    rigParent = None
    def __init__(self, side="C", legJnt=None, parent=None, root=None):
        if (parent!=None):
            if(leg.rigParent==None):
                leg.rigParent=mmod.transform(name="legGlobal", type="GRP", parent=parent.rigGrp)
        super(leg, self).__init__(side=side, jnt=legJnt, name="leg", segmentsList=["Hip", "Knee", "Ankle"], parent=leg.rigParent, root=root,  hook=parent.rootJnt)
        # FootRoll Attribute
        self.footRollAttr = self.effectorCtrl.addAttr(longName="footRoll", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        # RIBBON LIMBS
        self.femurRibbon =ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "femurRibbon", parent=leg.rigParent, root=fn.getChildren(root)[1], revolveVector=[0, 0, 1])
        self.tibiaRibbon =ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "tibiaRibbon", parent=leg.rigParent, root=fn.getChildren(root)[1], revolveVector=[0, 0, 1])
        # RIBBON VISIBILITY SWITCH
        mc.hide(self.femurRibbon.guides[0], self.femurRibbon.guides[-1], self.tibiaRibbon.guides[0], self.tibiaRibbon.guides[-1])
        ribbonVisibility = self.settingCtl.addAttr(longName = "secondaryControls", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)
        for femurControl, tibiaControl  in zip(self.femurRibbon.guides[1:-1], self.tibiaRibbon.guides[1:-1]):
            mmod.connectPlugs(ribbonVisibility, femurControl.visibility)
            mmod.connectPlugs(ribbonVisibility, tibiaControl.visibility)
 