import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import rigFn as rigFn 



def resetScapulaMod():
    scapula.rigParent=None
    scapula.ikHandleGrp = None
    scapula.controlGrp = None

class scapula(object):
    rigParent=None
    ikHandleGrp = None
    controlGrp = None
    
    def __init__(self, side="C", name="scapula", scapulaJnt=None, armJnt=None, parent=None, root=None):

        '''
        1. Creating Main Hierarchy from guides
        2. Scapula Set-Up
            2.1. Create IK Handle from start to end
            2.2. Create Ctrls
            2.3. Orient+point Constraint Ctrl > { ScapulaStartJNT, ArmStartJNT}
           
        '''
        # self
        self.side = side
        self.jntGuide = scapulaJnt
        
        self.parent = parent
        self.root = root
        self.name = name
                
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()

        if (self.parent!=None):
            if (scapula.rigParent==None):
                scapula.rigParent=mmod.transform(name="scapulaGlobal", type="GRP", parent=parent.rigGrp)
                mmod.connectAttr(fn.getParent(self.parent.rootJnt)+".scale", scapula.rigParent.name+".scale")

        if (scapulaJnt!=None):
            # 1. CREATING THE HIERARCHY
            if (scapula.ikHandleGrp==None):
                scapula.ikHandleGrp = mmod.transform(name="IKHandle", type="GRP", parent = scapula.rigParent)
                mc.parentConstraint (self.root, scapula.ikHandleGrp.name, mo=True)
               
            if(scapula.controlGrp==None):
                scapula.controlGrp  = mmod.transform(name=self.name+"Controller", type="GRP", parent = scapula.rigParent)
                mc.parentConstraint (self.parent.rootJnt, scapula.controlGrp)
                # scapula.controlGrp.addSpaceSwitch(spaceName = "root", parentObject=self.parent.rootJnt)
                # scapula.controlGrp.addSpaceSwitch(spaceName = "chest", parentObject=self.root)
                # mc.setAttr (spaceSwitch, 1)
            # GETTING GUIDE LIST
            self.jntGuideList = fn.descendentsList(root=self.jntGuide)

            self.jntChain = rigFn.createJntChain(self.jntGuideList ,side=self.side, name="bind"+self.name.capitalize(), parent=root)
            
            # 2.1. Creating IK Handle
            ik = rigFn.createIKHandle(self.jntChain[0], self.jntChain[-1], side=self.side, name=self.name+"IKHandle", parent=None)
            mc.parent(ik, scapula.ikHandleGrp)
            # 2.2. Creating CTRL
            # Creating guide
            #guideJnt = mmod.joint(side=self.side, name="scapulaGuide")
            #fn.snapTool(scapulaJnt, fn.getChildren(guideJnt))
            #mc.setAttr(guideJnt.name+".radius",  mc.getAttr(scapulaJnt+".radius"))
            scapulaFKCtl = rigFn.constructCTL(self.jntGuideList[1], side=self.side, name=self.name, parent=scapula.controlGrp)
            #mc.delete(guideJnt)
            
            # Creating guide
            guideJnt = mmod.joint(side=self.side, name="scapulaGuide")
            fn.snapTool(scapulaJnt, guideJnt)
            mc.setAttr(guideJnt.name+".radius",  mc.getAttr(scapulaJnt+".radius"))
            scapulaCtl = rigFn.constructCTL(guideJnt.name, side=self.side, name=self.name, parent=scapulaFKCtl)
            mc.delete(guideJnt)

            # Cleaning CTL
            mc.delete(fn.getChildren(scapulaCtl.name)[1])

            # Positioning CTL
            # fn.

            # 2.3. Constraints
            mc.pointConstraint(scapulaCtl, self.jntChain[0], mo=True)
            mc.orientConstraint(scapulaCtl, self.jntChain[0], mo=True)
            if (armJnt!=None):
                mc.pointConstraint(scapulaCtl, fn.getParent(armJnt.IKjntChain[0]), mo=True)
                mc.orientConstraint(scapulaCtl, fn.getParent(armJnt.IKjntChain[0]), mo=True)
                mc.pointConstraint(scapulaCtl, fn.getParent(armJnt.FKjntChain[0]), mo=True)
                # mc.orientConstraint(scapulaCtl, fn.getParent(armJnt.IKjntChain[0]), mo=True)
                mc.pointConstraint(scapulaCtl, fn.getParent(armJnt.bindJntChain[0]), mo=True)
                # mc.orientConstraint(scapulaCtl, armJnt.bindJntChain[0], mo=True)

            # # Constraining scapula Ctrl to Chest
            # mc.parentConstraint(self.root, fn.getParent(scapulaFKCtl.name), mo=True)     
            spaceSwitch = scapulaFKCtl.createSpaceSwitch()
            scapulaFKCtl.addSpaceSwitch(spaceName = "root", parentObject=self.parent.rootJnt)
            scapulaFKCtl.addSpaceSwitch(spaceName = "chest", parentObject=self.root)
            mc.setAttr (spaceSwitch, 1)       


        # DELETING GUIDES
        mc.delete(scapulaJnt)