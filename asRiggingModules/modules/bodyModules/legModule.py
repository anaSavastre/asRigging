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
import mayaNode as mNode



def resetLegMod():
    leg.rigParent = None
 
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
        # CREATING MAGNITUDE ATTR
        # Volume Preservation Attr
        volumePreservation =mc.addAttr(self.settingCtl.name, longName="volumePreservation", min=0, dv=1, max=1, at="short", keyable=True)


        self.femurRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "femurRibbon", parent=leg.rigParent, root=fn.getChildren(root)[1], revolveVector=[0, 0, 1])
        self.tibiaRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "tibiaRibbon", parent=leg.rigParent, root=fn.getChildren(root)[1], revolveVector=[0, 0, 1])
        
        # RIBBON VISIBILITY SWITCH
        mc.hide(self.femurRibbon.guides[0], self.femurRibbon.guides[-1], self.tibiaRibbon.guides[0], self.tibiaRibbon.guides[-1])
        ribbonVisibility = self.settingCtl.addAttr(longName = "secondaryControls", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)
        for femurControl, tibiaControl  in zip(self.femurRibbon.guides[1:-1], self.tibiaRibbon.guides[1:-1]):
            mmod.connectPlugs(ribbonVisibility, femurControl.visibility)
            mmod.connectPlugs(ribbonVisibility, tibiaControl.visibility)
 
        # CREATING VOLUME RESERVATION
        self.volumePreservationSetUp(self.femurRibbon, ribbonName="femur")
        self.volumePreservationSetUp(self.tibiaRibbon, ribbonName="tibia")
     