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
import rigFn as rigFn



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
        # aimGroup = mmod.transform(side=self.side, name="femurRibbonAim", type="GRP", parent = fn.getParent(self.femurRibbon.guides[0]))
        # mc.parent(self.femurRibbon.guides[0], aimGroup)
        # mc.aimConstraint(self.tibiaRibbon.ribbon.ribbonJoints[0],  aimGroup, aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root, mo=True)
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
