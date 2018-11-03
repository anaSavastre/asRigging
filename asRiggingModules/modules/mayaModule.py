import maya.cmds as mc
import maya.OpenMaya as om


def testProject():
    mc.file(new = True, f=True)
    grp = mc.group(em=True, n="C_grp_GRP")
    mc.xform(grp, t=[5, 0, 0])
    loc1 = locator ()
    loc2 = locator ()
    jnt1 = joint (parent=grp)
    jnt2 = joint ()
    loc3 = locator(parent=grp)
    mc.xform (loc1.name, t=[10, 0, 0])



class transform(object):

    elemIndex = 0
    nodeType = "transform"
    # visibility = 1
    # Main attributes
    def __init__(self, side="C", name="name", type="TRF", parent=None): 
        #, parent=None, position=[0, 0, 0]):
        self.side = side
        self.type = type
        self.name = side+"_"+name+"0"+str(self.elemIndex)+"_"+type
        transform.elemIndex+=1
        if (self.nodeType == "locator"):
            shapeNode = mc.createNode(self.nodeType, n=self.name.replace(name, name+"Shape"))
            mc.rename(mc.listRelatives(shapeNode, p=True), self.name)
        elif (self.nodeType == "nurbsCurve"):
            # print "name", self.name
            makeCircleNode = mc.createNode("makeNurbCircle", name="make_"+self.name)
            shapeNode = mc.createNode(self.nodeType, n=self.name.replace(name, name+"Shape"))
            mc.connectAttr(makeCircleNode+".outputCurve", shapeNode+".create")
            mc.rename(mc.listRelatives(shapeNode, p=True), self.name)
        else:
            mc.createNode(self.nodeType, n=self.name)
        
        if (parent != None):
            mc.parent(self.name, parent)
            mc.setAttr(self.name+".translateX",0)
            mc.setAttr(self.name+".translateY",0)
            mc.setAttr(self.name+".translateZ",0)
            if (self.nodeType == "joint"):
                mc.setAttr(self.name+".jointOrientX", 0)
                mc.setAttr(self.name+".jointOrientY", 0)
                mc.setAttr(self.name+".jointOrientZ", 0)
            self.parent = parent

    # Add Attribute
    def addAttr(self, longName="attr", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="double", keyable=True):
        attr = mc.addAttr(ln=longName, smn=softMinValue, dv=defaultValue, smx=softMaxValue, at=attrType, k=keyable)
        return "{}.{}".format(self.name, longName)
        
    
    # TranslateX
    @property
    def translateX(self):
        return mc.getAttr(self.name+".translateX")
    @translateX.setter
    def translateX(self, value):
        mc.setAttr(self.name+".translateX", value)

    # TranslateY
    @property
    def translateY(self):
        return mc.getAttr(self.name+".translateY")
    @translateY.setter
    def translateY(self, value):
        mc.setAttr(self.name+".translateY", value)

    # TranslateZ
    @property
    def translateZ(self):
        return mc.getAttr(self.name+".translateZ")
    @translateZ.setter
    def translateZ(self, value):
        mc.setAttr(self.name+".translateZ", value)

    # Visibility
    @property
    def visibility(self):
        return mc.getAttr(self.name+".visibility")
    @visibility.setter
    def visibility(self, value):
        mc.setAttr(self.name+".visibility", value)

    # Operator Overloading
    # def __gt__(self, firstAttr, anotherAttr):
    #     mc.connectAttr("{}.{}".format(self.name, firstAttr), anotherAttr, f=True)

    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

    # Operator Overloading
    # def __lt__(self):
        


class locator(transform):

    elemIndex = 0
    nodeType = "locator"
    def __init__(self, side="C", name="locator", type="LOC", parent=None): #, parent=None, position=[0, 0, 0]):
        super(locator, self).__init__(side, name, type, parent)
        locator.elemIndex +=1
      
class joint(transform):

    elemIndex = 0
    nodeType = "joint"
    def __init__(self, side="C", name="joint", type="JNT", parent=None): #, parent=None, position=[0, 0, 0]):
        super(joint, self).__init__(side, name, type, parent)
        joint.elemIndex +=1
    
class circle(transform):
    elemIndex = 0
    nodeType = "nurbsCurve"
    def __init__(self, side="C", name="circle", type="CTL", parent=None): #, parent=None, position=[0, 0, 0]):
        super(circle, self).__init__(side, name, type, parent)
        circle.elemIndex +=1


# # loc = locator()
c = circle(name="ana")