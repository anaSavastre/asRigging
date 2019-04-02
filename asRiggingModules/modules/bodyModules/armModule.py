
import maya.cmds as mc
import mayaModule as mmod
import mayaNode as mNode
import functions as fn
import blendFKIK as blendFKIK
import ribbonLimbs as ribbonLimbs
import rigFn as rigFn




def resetArmMod():
    arm.rigParent = None

 
class arm(blendFKIK.blendFKIK):
    '''
    side = Arm side (L, R, C)
    armJnt = guideJnt (first jnt in chain)
    parent = rig class 
    root = parent of bind Jnts (under what jnt does the user want the joints to be created)
    '''
    rigParent=None
    def __init__(self, side="C", armJnt = None, parent=None, root=None):
        if (parent!=None):
            if (arm.rigParent==None):
                arm.rigParent=mmod.transform(name="armGlobal", type="GRP", parent=parent.rigGrp)
        try:
            self.root = root.clavicleControl[1]
        except:
            self.root = root
        super(arm, self).__init__(side=side, jnt=armJnt, name="arm", segmentsList=["Shoulder", "Elbow", "Wrist"], parent=arm.rigParent, root=self.root, hook=parent.rootJnt)


        # GLOBALS
        self.arm = root
        # RIBBON LIMBS
        self.armRibbonGrp = mmod.transform(side=self.side, name="ribbonArm", type="GRP", parent = arm.rigParent)
        self.humerusRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "humerusRibbon", parent=self.armRibbonGrp, root=fn.getParent(root.clavicleControl[1]), revolveVector=[0, 0, 1])
        self.radiusRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "radiusRibbon", parent=self.armRibbonGrp, root=fn.getParent(root.clavicleControl[1]), revolveVector=[0, 0, 1])
        # Volume Preservation Attr
        volumePreservation =mc.addAttr(self.settingCtl.name, longName="volumePreservation", min=0, dv=0, max=1, at="short", keyable=True)

      
        # # WRIST TWIST TO RIBBON RADIUS
        # self.twistArm()
        # CLAVICLE AIM
        self.aimClavicle()
        # VISIBILITY SWITCH ATTR
        ribbonVisibility = self.settingCtl.addAttr(longName = "secondaryControls", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)

        # CREATING VOLUME RESERVATION
        self.volumePreservationSetUp(self.humerusRibbon, ribbonName="humerus")
        self.volumePreservationSetUp(self.radiusRibbon, ribbonName="radius")
        # CONSTRANING ARM TO CLAVICLE
        # mc.orientConstraint (self.root, fn.getParent(self.humerusRibbon.guides[0]), mo=True)
        rigFn.parentConstraintMO (self.root.name, fn.getParent(fn.getParent(self.humerusRibbon.guides[0])), fn.getParent(self.humerusRibbon.guides[0]), translate=False, rotate=True, scale=False )
        # # AIM HUMERUS CTRLS TO ELBOW
        aimGroup = mmod.transform(side=self.side, name="humerusRibbonAim", type="GRP", parent = fn.getParent(self.humerusRibbon.guides[0]))
        mc.parent(self.humerusRibbon.guides[0], aimGroup)
        mc.aimConstraint(self.radiusRibbon.ribbon.ribbonJoints[0],  aimGroup, aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root, mo=True)
        # ELBOW CONTROL
        rigFn.parentConstraintMO(self.radiusRibbon.guides[0].name, fn.getParent(self.humerusRibbon.guides[-1]), self.humerusRibbon.guides[-1].name, maintainOffset = True, translate=True, rotate=True, scale=False)
        # RIBBON GLOBAL
        self.ribbonGlobalCtrl()
        
        # for guide in self.humerusRibbon.guides:
        #     aimGroup = mmod.transform(side=self.side, name="ribbonAim", type="GRP", parent = fn.getParent(guide))
        #     mc.parent(guide, aimGroup)
        #     mc.aimConstraint(self.radiusRibbon.ribbon.ribbonJoints[0],  aimGroup, aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root)
        # # AIM RADIUS CTRLS TO ELBOW
        # for guide in self.radiusRibbon.guides[1:]:
        #     aimGroup = mmod.transform(side=self.side, name="ribbonAim", type="GRP", parent = fn.getParent(guide))
        #     mc.parent(guide, aimGroup)
        #     mc.aimConstraint(self.radiusRibbon.ribbon.ribbonJoints[0],  aimGroup, mo=True, aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root)
     
        # SPACE SWITCH
        self.effectorCtrl.createSpaceSwitch()
        self.effectorCtrl.addSpaceSwitch (spaceName = "clavicle", parentObject = self.root)
        self.effectorCtrl.addSpaceSwitch (spaceName = "chest", parentObject = root.root)

        # RIBBON VISIBILITY SWITCH
        mc.hide(self.humerusRibbon.guides[0], self.humerusRibbon.guides[-1], self.radiusRibbon.guides[0], self.radiusRibbon.guides[-1])
        for humerusControl, radiusControl  in zip(self.humerusRibbon.guides[1:-1], self.radiusRibbon.guides[1:-1]):
            mmod.connectPlugs(ribbonVisibility, humerusControl.visibility)
            mmod.connectPlugs(ribbonVisibility, radiusControl.visibility)
        mmod.connectPlugs(ribbonVisibility, self.radiusRibbon.guides[0].visibility)
        mmod.connectPlugs(ribbonVisibility, self.globalRibbonCtrl.visibility)

    
    
    def ribbonGlobalCtrl (self):
        # Creating Control
        self.globalRibbonCtrl = rigFn.constructCTL(fn.getChildren(self.radiusRibbon.guides[0].name)[1], side=self.side, name="armRibbonGlobal", parent=self.armRibbonGrp, ctrlScale=1, ctrlShape=0)
        fn.scaleShapePoints(fn.getChildren(self.globalRibbonCtrl)[0], 10)
        # Connecting Control To Ribbon System
        # Elbow Ctrl
        guide = self.radiusRibbon.guides[0]
        connectionsGrp = mmod.transform(side=self.side, name="armRlobalConnection", type="GRP", parent = fn.getParent(guide))
        mc.parent(guide, connectionsGrp)
        mmod.connectAttr(self.globalRibbonCtrl.name+".translate", connectionsGrp.name+".translate")
        # 1. Creating Connection Grps
        # Hummerus Guide
        connectionsGrpHumerus = mmod.transform(side=self.side, name="armGlobalConnection", type="GRP", parent = fn.getParent(self.humerusRibbon.guides[2]))
        mc.parent(self.humerusRibbon.guides[2], connectionsGrpHumerus)
        # Radius Guide
        connectionsGrpRadius = mmod.transform(side=self.side, name="armGlobalConnection", type="GRP", parent = fn.getParent(self.radiusRibbon.guides[2]))
        mc.parent(self.radiusRibbon.guides[2], connectionsGrpRadius)
        # 2. Creating Weight Attr
        globalCtlWeight = self.settingCtl.addAttr(longName = "ribbonGlobWeight", softMinValue=-1, defaultValue=0.25, softMaxValue=1, attrType="double", keyable=True)
        # 3. Multiply divide node
        multiplyDivideNode = mNode.multiplyDivide(side=self.side, name=self.name+"ribbonGlobalCtrlWeigth")
        # 4. Connections
        mmod.connectAttr(self.globalRibbonCtrl.name+".translate", multiplyDivideNode.getInput1())
        mmod.connectAttr(self.settingCtl.name+".ribbonGlobWeight", multiplyDivideNode.name+".input2X")
        mmod.connectAttr(self.settingCtl.name+".ribbonGlobWeight", multiplyDivideNode.name+".input2Y")
        mmod.connectAttr(self.settingCtl.name+".ribbonGlobWeight", multiplyDivideNode.name+".input2Z")
        mmod.connectAttr(multiplyDivideNode.getOutput(), connectionsGrpHumerus.name+".translate")
        mmod.connectAttr(multiplyDivideNode.getOutput(), connectionsGrpRadius.name+".translate")        

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

    
    def aimClavicle(self):
        if ("bindClavicle" in self.root.name):
            # CREATE SWITCH ATTR
            autoClavSwitch =mc.addAttr(self.settingCtl.name, longName="autoClavicle", min=0, dv=1, max=1, at="short", keyable=True)
            clavFollowAmount = mc.addAttr(self.settingCtl.name, longName="clavicleFallowAmount", min=0, dv=0.5, at="double", keyable=True)
            # LIMIT AIM GRP TRANSLATION
            # REDUCE WRIST TRANSFORMATION
            reduceWristTransformation =mNode.multDoubleLinear(side =self.side, name="wristTransformation")
            # CONNECTIONS
            mmod.connectAttr(self.effectorCtrl.name+".translateY", reduceWristTransformation.getInput1())
            mmod.connectAttr(self.settingCtl.name+".clavicleFallowAmount", reduceWristTransformation.getInput2())
            # SWITCH
            multDoubleLin = mNode.multDoubleLinear(side=self.side, name=self.name+"AutoClavicleSwitch")
            mmod.connectAttr(reduceWristTransformation.getOutput(), multDoubleLin.getInput1())
            mmod.connectAttr(self.settingCtl.name+".autoClavicle", multDoubleLin.getInput2())
            mmod.connectAttr(multDoubleLin.getOutput(), self.arm.aimObject.name+".translateY")
            
         
    def twistConnection(self, targetParent, object):
        objParent = fn.getParent(object)
        # Matrix Mult
        side = fn.concat_str(str1 = object, s1_begin=0, s1_end=len(object)-1 )
        matrix = mNode.multMatrix(side=side, name="transformationMatrix")
        # GETTING LOCAL OFFSET
        localOffset = fn.getLocalOffset(objParent, object)
        mc.setAttr(matrix.name+".matrixIn[0]", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")


        mmod.connectAttr(targetParent+".worldMatrix", matrix.name+".matrixIn[1]")
        mmod.connectAttr(objParent+".worldInverseMatrix", matrix.name+".matrixIn[2]")
        decomposeMatrix = mNode.decomposeMatrix(side=side, name="transformation")
        mmod.connectAttr(matrix.getMatrixSum(), decomposeMatrix.getInputMatrix())
        mmod.connectAttr(decomposeMatrix.name+".outputRotateX", object+".rotateX")
    def twistArm(self):
        # self.twistConnection(self.effectorCtrl.name, self.radiusRibbon.guides[-1].name )
        mc.orientConstraint(self.effectorCtrl.name, self.radiusRibbon.guides[-1].name, mo=True)
      

