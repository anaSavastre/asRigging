
import maya.cmds as mc
import mayaModule as mmod
import blendFKIK as blendFKIK



def resetArmMod():
    arm.rigParent = None

class arm(blendFKIK.blendFKIK):
    rigParent=None
    def __init__(self, side="C", armJnt = None, parent=None, root=None):
        if (parent!=None):
            if (arm.rigParent==None):
                arm.rigParent=mmod.transform(name="armGlobal", type="GRP", parent=parent.rigGrp)

        super(arm, self).__init__(side=side, jnt=armJnt, name="arm", segmentsList=["Shoulder", "Elbow", "Wrist"], parent=arm.rigParent, root=root, hook=parent.rootJnt)

    