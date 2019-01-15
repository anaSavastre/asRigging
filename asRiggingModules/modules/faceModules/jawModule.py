import maya.cmds as mc
import rigFn as rigFn
import mayaModule as mmod
import mayaNode as mNode
import functions as fn


class jaw(object):
    def __init__(self, side="C", name="jaw", jawJnt=None, root=None, parent=None, hook=None):
        '''
        JAW MODULE
    
        '''
        
        # GLOBALS
        self.side = side
        self.name = name
        self.root = root
        self.parent = parent
        self.hook = hook
        self.guides = fn.descendentsList(root=jawJnt)
        self.neckJnt = []
        mmod.resetCount() 
        # 1. CREATE JNT HIERARCHY
        # 1.0. JAW 
        self.jawJnt = rigFn.constructJNT(self.guides[0], side=self.side, name="bind"+self.name.capitalize(), parent = self.root)
        self.jawCtrl = rigFn.constructCTL(self.guides[-1], name = "bind"+self.name.capitalize(), parent = self.root)
        print fn.getChildren(self.jawCtrl.name)[1]
        mc.parent (fn.getChildren(self.jawCtrl.name)[1], self. jawJnt.name)

        # 2. CONNECT CTRL TO JAW ROTATION
        # CREATE REST POSE GUIDES
        jawRest = mmod.transform(side=self.side, name="jawRestGuide", type="GRP", parent = self.guides[0])
        mc.parent (jawRest.name, fn.getChildren(self.root)[1])
        jawCtrlRest = mmod.transform(side=self.side, name="jawCtrlRestGuide", type="GRP", parent = self.guides[1])
        mc.parent (jawCtrlRest.name, fn.getChildren(self.root)[1])
        # GET REST POSE VECTOR
        # ctrlPoz = mc.xform(self.jawCtrl.name, q=True, t=True, ws=True) 
        # jntPoz = mc.xform(self.jawJnt.name, q=True, t=True, ws=True)
        # restPoseVector = [ctrlPoz[0]-jntPoz[0], ctrlPoz[1]-jntPoz[1], ctrlPoz[2]-jntPoz[2]]
        # print restPoseVector


        worldMatrixCtrl = mNode.decomposeMatrix(side=self.side, name=self.name+"RestCtlWM")
        mmod.connectAttr(jawCtrlRest.name+".worldMatrix", worldMatrixCtrl.getInputMatrix())        
        worldMatrixJnt = mNode.decomposeMatrix(side=self.side, name=self.name+"RestJntWM")
        mmod.connectAttr(jawRest.name+".worldMatrix", worldMatrixJnt.getInputMatrix())
        restVect = mNode.plusMinusAverage(side=self.side, name=self.name+"RestVect")
        mc.setAttr(restVect.getOperation(), 2)
        mmod.connectAttr(worldMatrixCtrl.getOutputTranslate(), restVect.name+".input3D[0]")
        mmod.connectAttr(worldMatrixJnt.getOutputTranslate(), restVect.name+".input3D[1]")

        # TRANSFORMATION VECTOR
        worldMatrixCtrl = mNode.decomposeMatrix(side=self.side, name=self.name+"CtlWM")
        mmod.connectAttr(self.jawCtrl.name+".worldMatrix", worldMatrixCtrl.getInputMatrix())        
        # worldMatrixJnt = mNode.decomposeMatrix(side=self.side, name=self.name+"JntWM")
        mmod.connectAttr(jawRest.name+".worldMatrix", worldMatrixJnt.getInputMatrix())
        transformVect = mNode.plusMinusAverage(side=self.side, name=self.name+"TransformationVect")
        mc.setAttr(transformVect.getOperation(), 2)
        mmod.connectAttr(worldMatrixCtrl.getOutputTranslate(), transformVect.name+".input3D[0]")
        mmod.connectAttr(worldMatrixJnt.getOutputTranslate(), transformVect.name+".input3D[1]")

        # CALCULATING ANGLE BETWEEN
        angleBetween = mNode.angleBetween(side=self.side, name="jawRotationAngle")
        mmod.connectAttr(restVect.getOutput3D(), angleBetween.getVector1())
        mmod.connectAttr(transformVect.getOutput3D(), angleBetween.getVector2())
        # CONNECTING ROTATION
        inverseX = mNode.animBlendNodeAdditiveDA(side=self.side, name=self.name+"InverseRotX")
        mmod.connectAttr(angleBetween.name+".eulerZ", self.jawJnt.name+".rotateX")
        mmod.connectAttr(angleBetween.name+".eulerY", self.jawJnt.name+".rotateY")
        mmod.connectAttr(angleBetween.name+".eulerX", inverseX.getInputA())
        mc.setAttr(inverseX.getWeightA(), -1)
        mmod.connectAttr(inverseX.getOutput() , self.jawJnt.name+".rotateZ")

        # DELETING GUIDE
        mc.delete(self.guides[0])
