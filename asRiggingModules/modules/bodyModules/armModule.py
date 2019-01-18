
import maya.cmds as mc
import mayaModule as mmod
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

        super(arm, self).__init__(side=side, jnt=armJnt, name="arm", segmentsList=["Shoulder", "Elbow", "Wrist"], parent=arm.rigParent, root=root, hook=parent.rootJnt)
        # RIBBON LIMBS
        self.humerusRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "humerusRibbon", parent=arm.rigParent, root=root, revolveVector=[0, 0, 1])
        self.radiusRibbon = ribbonLimbs.ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "radiusRibbon", parent=arm.rigParent, root=root, revolveVector=[0, 0, 1])
        # RIBBON VISIBILITY SWITCH
        mc.hide(self.humerusRibbon.guides[0], self.humerusRibbon.guides[-1], self.radiusRibbon.guides[0], self.radiusRibbon.guides[-1])
        ribbonVisibility = self.settingCtl.addAttr(longName = "secondaryControls", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)
        for humerusControl, radiusControl  in zip(self.humerusRibbon.guides[1:-1], self.radiusRibbon.guides[1:-1]):
            mmod.connectPlugs(ribbonVisibility, humerusControl.visibility)
            mmod.connectPlugs(ribbonVisibility, radiusControl.visibility)
