import maya.cmds as mc
import functions as fn
import mayaModule as mmod
import rigFn



class clavicle(object):
    def __init__(self, side="C", name="clavicle", clavicleJnt=None, parent=None, root=None):
        
        '''
        1. Creating Main Hierarchy from guides
        2. Clavicle Set-Up
            2.2. Create Ctrl
        
        '''
        self.side = side
        self.name = name
        self.jntGuide = clavicleJnt
        self.parent = parent
        self.root = root
        
        if (clavicleJnt!=None):
            self.jntGuideList = fn.descendentsList(root=self.jntGuide)
            self.clavicleControl = rigFn.createFKChain(self.jntGuideList, side= self.side, name="bind"+self.name.capitalize(), parent=self.root)
            # POSITIONING CONTROL
            fn.translateShapePoints(fn.getChildren(self.clavicleControl[0])[0], [mc.getAttr(fn.getParent(self.clavicleControl[1])+".translateX"), 0, 0], 0)
            # CREATE AIMING CONTROL
            self.aimingSystem()
            # DELETING GUIDES
            mc.delete(self.jntGuide)
    def aimingSystem (self):
        clavicleAimGrp = mmod.transform(side=self.side, name=self.name+"AimSyatem", type="GRP", parent= fn.getParent(fn.getParent(self.clavicleControl)))
        aimObject = mmod.transform(side =self.side, name="clavicleAim", parent= self.jntGuideList[-1])
        upObj = mmod.transform(side =self.side, name="clavicleUp", parent=self.jntGuideList[0])
        fn.snapTool(self.jntGuideList[-1], aimObject)
        fn.snapTool(self.jntGuideList[0], upObj)
        translationAmouunt = mc.getAttr(self.jntGuideList[0]+".radius")
        xDirection = fn.vectorBetween (mc.xform(self.jntGuideList[0], ws=True, q=True, t=True), mc.xform(self.jntGuideList[1], ws=True, q=True, t=True))
        mc.xform(upObj, r=True, t =[0, translationAmouunt, 0])
        mc.xform(aimObject, r=True, t =[translationAmouunt*xDirection[0], 0, 0])
        mc.parent ([aimObject, upObj], clavicleAimGrp)
        mc.makeIdentity([aimObject, upObj], a=True, t=True, r=True)
        mc.aimConstraint(aimObject, fn.getParent(self.clavicleControl), aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject = upObj,  mo=True)
        self.aimObject = aimObject


