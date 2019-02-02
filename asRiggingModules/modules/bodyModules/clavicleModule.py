import maya.cmds as mc
import finctions as fn
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
            # DELETING GUIDES
            mc.delete(self.jntGuide)