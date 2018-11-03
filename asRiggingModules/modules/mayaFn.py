import maya.cmds as mc


mc.file(new = True, f=True)



class mayaObject(object):

    elemIndex = 0
    nodeType = "transform"

    def __init__(self, side="C", name="name", type="MOBJ", parent=None): 
        #, parent=None, position=[0, 0, 0]):
        self.side = side
        self.type = type
        self.name = side+"_"+name+str(self.elemIndex)+"_"+type
        mayaObject.elemIndex+=1
        mc.createNode(self.nodeType, n=self.name)
        if (parent != None):
            mc.parent(self.name, parent)
            mc.setAttr(self.name+".translateX",0)
            self.parent = parent



class locator(mayaObject):

    elemIndex = 0
    nodeType = "locator"
    def __init__(self, side="C", name="locator", type="LOC", parent=None): #, parent=None, position=[0, 0, 0]):
        super(locator, self).__init__(side, name, type, parent)
        locator.elemIndex +=1
      
class joint(mayaObject):

    elemIndex = 0
    nodeType = "joint"
    def __init__(self, side="C", name="joint", type="JNT", parent=None): #, parent=None, position=[0, 0, 0]):
        super(joint, self).__init__(side, name, type, parent)
        joint.elemIndex +=1
    

grp = mc.group(em=True, n="C_grp_GRP")
mc.xform(grp, t=[5, 0, 0])
loc1 = locator ()
loc2 = locator ()
jnt1 = joint (parent=grp)
jnt2 = joint ()
mc.xform (loc1.name, t=[10, 0, 0])