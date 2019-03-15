
import maya.cmds as mc
import mayaModule as mmod
import mayaNode as mNode
import functions as fn
import blendFKIK as blendFKIK
import ribbonLimbs as ribbonLimbs




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

        super(arm, self).__init__(side=side, jnt=armJnt, name="arm", segmentsList=["Shoulder", "Elbow", "Wrist"], parent=arm.rigParent, root=root.clavicleControl[1], hook=parent.rootJnt)
        # GLOBALS
        self.arm = root
        # RIBBON LIMBS
        self.humerusRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "humerusRibbon", parent=arm.rigParent, root=fn.getParent(root.clavicleControl[1]), revolveVector=[0, 0, 1])
        self.radiusRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "radiusRibbon", parent=arm.rigParent, root=fn.getParent(root.clavicleControl[1]), revolveVector=[0, 0, 1])
        # CREATING VOLUME RESERVATION
        volumePreservation =mc.addAttr(self.settingCtl.name, longName="volumePreservation", min=-2, dv=0, max=2, at="double", keyable=True)

        self.volumePreservationSetUp(self.humerusRibbon, ribbonName="humerus")
        self.volumePreservationSetUp(self.radiusRibbon, ribbonName="tibia")
       
        # RIBBON VISIBILITY SWITCH
        mc.hide(self.humerusRibbon.guides[0], self.humerusRibbon.guides[-1], self.radiusRibbon.guides[0], self.radiusRibbon.guides[-1])
        ribbonVisibility = self.settingCtl.addAttr(longName = "secondaryControls", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)
        for humerusControl, radiusControl  in zip(self.humerusRibbon.guides[1:-1], self.radiusRibbon.guides[1:-1]):
            mmod.connectPlugs(ribbonVisibility, humerusControl.visibility)
            mmod.connectPlugs(ribbonVisibility, radiusControl.visibility)
        # # WRIST TWIST TO RIBBON RADIUS
        # self.twistArm()
        # CLAVICLE AIM
        self.aimClavicle()
        # SPACE SWITCH
        self.effectorCtrl.createSpaceSwitch()
        self.effectorCtrl.addSpaceSwitch (spaceName = "chest", parentObject = self.root)
    def aimClavicle(self):
        if ("L_bindClavicle" in self.root.name):
            # LIMIT AIM GRP TRANSLATION
            # REDUCE WRIST TRANSFORMATION
            reduceWristTransformation =mNode.multDoubleLinear(side =self.side, name="wristTransformation")
            # CONNECTIONS
            mmod.connectAttr(self.effectorCtrl.name+".translateY", reduceWristTransformation.getInput1())
            mc.setAttr(reduceWristTransformation.getInput2(), 0.1)
            mmod.connectAttr(reduceWristTransformation.getOutput(), self.arm.aimObject.name+".translateY")
            
        
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
        for i in range (6):
            attrName = ribbonName+"RibbonMagnitude"+str(i)
            magnitudeAttr =mc.addAttr(self.settingCtl.name, longName=attrName, min=-2, dv=0, max=2, at="double", keyable=True)
            powerNode = mNode.multiplyDivide(side=self.side, name=self.name+ribbonName.capitalize()+"PowerNode")
            mmod.connectAttr(condNode.name+".outColorR", powerNode.name+".input1X")
            mmod.connectAttr(self.settingCtl.name+"."+attrName, powerNode.name+".input2X")
            powerNode.operation = 3
            # Connecting To JNT Scale
            mmod.connectAttr(powerNode.name+".outputX",  ribbonLimb.ribbon.ribbonJoints[i].name+".scaleY")
            mmod.connectAttr(powerNode.name+".outputX",  ribbonLimb.ribbon.ribbonJoints[i].name+".scaleZ")
      
