import maya.cmds as mc
import maya.OpenMaya as om

import functions as fn
import mayaNode as mNode

def getParent(grp):
    '''
    Returns parent of given transform node in the outliner 
    '''
    return mc.listRelatives(grp, p=True)

def resetCount():
    resetJNTCount()
    resetTRNCount()
    resetLOCCount()
    resetCTLCount()
def resetJNTCount():
    joint.elemIndex = 0
def resetCTLCount():
    circle.elemIndex = 0
def resetTRNCount():
    transform.elemIndex = 0
def resetLOCCount():
    locator.elemIndex = 0

def connectAttr(attr1, attr2):
    mc.connectAttr(attr1, attr2, f=True)

def connectPlugs(plug1, plug2):
    dgModifier = om.MDGModifier()
    dgModifier.connect(plug1, plug2)
    dgModifier.doIt()

class transform(object):

    elemIndex = 0
    nodeType = "transform"
    # visibility = 1
    # Main attributes
    def __init__(self, side="C", name="name", type="TRF", parent=None): 
        self.side = side
        self.type = type
        self.name = side+"_"+name+"0"+str(self.elemIndex)+"_"+type
        if (type == "GRP" or type == "OFS" or type == "TRF"):
            transform.elemIndex+=1
        self.transformNode = mc.createNode(self.nodeType, n=self.name)
        if (parent != None):
            if(getParent(self.name)!=None):
                transformName = getParent(self.name)[0]
            else:
                transformName = self.name
            mc.parent(transformName, parent)
            mc.setAttr(transformName+".translateX",0)
            mc.setAttr(transformName+".translateY",0)
            mc.setAttr(transformName+".translateZ",0)
            mc.setAttr(transformName+".rotateX",0)
            mc.setAttr(transformName+".rotateY",0)
            mc.setAttr(transformName+".rotateZ",0)
            self.parent = parent
        
    # Add Attribute
    def getPlug(self, nodeName):
        ''' returns node's plug '''
        self_mObject =self.getMObject()
        dependencyNode =om.MFnDependencyNode(self_mObject)
        try:
            plug = dependencyNode.findPlug(nodeName)
            return plug
        except:
            return None

    def addAttr(self, longName="attr", softMinValue=None, defaultValue=0, softMaxValue=None, attrType="double", keyable=True):
        if softMaxValue!=None:
            attr = mc.addAttr(self.name, ln=longName, smn=softMinValue, dv=defaultValue, smx=softMaxValue, at=attrType, k=keyable)
        else:
            attr = mc.addAttr(self.name, ln=longName, at=attrType, dv=defaultValue, k=keyable)
        # return "{}.{}".format(self.name, longName)
        return self.getPlug(longName)
        
    def getMObject(self):
        selectionList = om.MSelectionList()
        try: 
            selectionList.add(self.name)
            mObj = om.MObject()
            selectionList.getDependNode(0, mObj)
            return mObj
        except:
            return None
    
  
    # Translate
    def getTranslate(self):
        return mc.getAttr(self.name+".translate")
    @property
    def translate(self):
        ''' returns node's plug '''
        return self.getPlug("translate")
    @translate.setter
    def translate(self, value):
        mc.setAttr(self.name+".translate", value)
    
    # TranslateX
    def getTranslateX(self):
        return mc.getAttr(self.name+".translateX")
    @property
    def translateX(self):
        ''' returns node's plug '''
        return self.getPlug("translateX")
    @translateX.setter
    def translateX(self, value):
        mc.setAttr(self.name+".translateX", value)

    # TranslateY
    @property
    def translateY(self):
        ''' returns node's plug '''
        return self.getPlug("translateY")

    @translateY.setter
    def translateY(self, value):
        mc.setAttr(self.name+".translateY", value)

    def getTranslateY(self):
        return mc.getAttr(self.name+".translateY")

    # TranslateZ
    @property
    def translateZ(self):
        ''' returns node's plug '''
        return self.getPlug("translateZ")
    @translateZ.setter
    def translateZ(self, value):
        mc.setAttr(self.name+".translateZ", value)
    
    def getTranslateZ(self):
        return mc.getAttr(self.name+".translateZ")

    # ROTATION
    # rotate
    @property
    def rotate(self):
        ''' returns node's plug '''
        return self.getPlug("rotate")
    @rotate.setter
    def rotate(self, value):
        mc.setAttr(self.name+".rotate", value)
    
    def getrotate(self):
        return mc.getAttr(self.name+".rotate")
    # rotateX
    @property
    def rotateX(self):
        ''' returns node's plug '''
        return self.getPlug("rotateX")
    @rotateX.setter
    def rotateX(self, value):
        mc.setAttr(self.name+".rotateX", value)
    
    def getRotateX(self):
        return mc.getAttr(self.name+".rotateX")

    # rotateY
    @property
    def rotateY(self):
        ''' returns node's plug '''
        return self.getPlug("rotateY")
    @rotateY.setter
    def rotateY(self, value):
        mc.setAttr(self.name+".rotateY", value)
    
    def getRotateY(self):
        return mc.getAttr(self.name+".rotateY")

    # rotateZ
    @property
    def rotateZ(self):
        ''' returns node's plug '''
        return self.getPlug("rotateZ")
    @rotateZ.setter
    def rotateZ(self, value):
        mc.setAttr(self.name+".rotateZ", value)
    
    def getRotateZ(self):
        return mc.getAttr(self.name+".rotateZ")



    # SCALE
    # scale
    @property
    def scale(self):
        ''' returns node's plug '''
        return self.getPlug("scale")
    @scale.setter
    def scale(self, value):
        mc.setAttr(self.name+".scale", value)
    
    def getscale(self):
        return mc.getAttr(self.name+".scale")
    # scaleX
    @property
    def scaleX(self):
        ''' returns node's plug '''
        return self.getPlug("scaleX")
    @scaleX.setter
    def scaleX(self, value):
        mc.setAttr(self.name+".scaleX", value)
    
    def getRotateX(self):
        return mc.getAttr(self.name+".scaleX")

    # scaleY
    @property
    def scaleY(self):
        ''' returns node's plug '''
        return self.getPlug("scaleY")
    @scaleY.setter
    def scaleY(self, value):
        mc.setAttr(self.name+".scaleY", value)
    
    def getRotateY(self):
        return mc.getAttr(self.name+".scaleY")

    # scaleZ
    @property
    def scaleZ(self):
        ''' returns node's plug '''
        return self.getPlug("scaleZ")
    @scaleZ.setter
    def scaleZ(self, value):
        mc.setAttr(self.name+".scaleZ", value)
    
    def getRotateZ(self):
        return mc.getAttr(self.name+".scaleZ")


    # Visibility
    def getVisibility(self):
        return mc.getAttr(self.name+".visibility")
    @property
    def visibility(self):
        ''' returns node's plug '''
        return self.getPlug("visibility")
    @visibility.setter
    def visibility(self, value):
        mc.setAttr(self.name+".visibility", value)

    # WorldMatrix
    def getWorldMatrix(self):
        return self.name+".worldMatrix"
    @property
    def worldMatrix(self):
        return self.getPlug("worldMatrix")
    @worldMatrix.setter
    def worldMatrix(self, matrix):
        mc. setAttr(self.name+".worldMatrix", matrix)
    def __repr__(self):
        return self.name
    def __str__(self):
        return self.name

    def createSpaceSwitch (self, attrName = "spaceSwitch", enumName="world"):
        self.spaceSwitch = attrName
        self.enumName = enumName
        self.spaceIndex = 0
        mc.addAttr(self.name, ln = attrName, enumName = self.enumName, at="enum", k=True)
        return self.name+"."+self.spaceSwitch

    def addSpaceSwitch(self, spaceName = "space", parentObject=None):
        mc.addAttr (self.name+"."+self.spaceSwitch, e=True, enumName=self.enumName+":"+spaceName)
        self.enumName += ":"+spaceName
        self.spaceIndex += 1
        if (parentObject!=None):
            constraint = mc.parentConstraint(parentObject, fn.getParent(self.name), mo=True)[0]
            constraintWeightAlias = mc.parentConstraint(constraint, q=True, wal=True)[self.spaceIndex-1]
            conditionNode = mNode.condition(side=self.side, name="spaceSwitch"+spaceName.capitalize())
            connectAttr(self.name+"."+self.spaceSwitch, conditionNode.getFirstTerm())
            conditionNode.secondTerm = self.spaceIndex
            mc.setAttr(conditionNode.name+".colorIfTrueR", 1)
            mc.setAttr(conditionNode.name+".colorIfFalseR", 0)
            connectAttr(conditionNode.name+".outColorR", constraint+"."+constraintWeightAlias)
            




class locator(transform):

    elemIndex = 0
    nodeType = "locator"
    def __init__(self, side="C", name="locator", type="LOC", parent=None):
        super(locator, self).__init__(side, name+"Shape", type, parent)
        locator.elemIndex +=1
        name = self.name
        self.name = name.replace("Shape", "")
      
class joint(transform):

    elemIndex = 0
    nodeType = "joint"
    def setColor(self, colorNumber):
        mc.setAttr(self.name+".overrideEnabled", 1);
        #set color to yellow
        mc.setAttr(self.name+".overrideColor", colorNumber)
    def __init__(self, side="C", name="joint", type="JNT", parent=None): 
        super(joint, self).__init__(side, name, type, parent)
        joint.elemIndex +=1
        if (parent!=None):                
            mc.setAttr(self.name+".jointOrientX", 0)
            mc.setAttr(self.name+".jointOrientY", 0)
            mc.setAttr(self.name+".jointOrientZ", 0)
        
        # Coloring JNT
        if (self.side == "C"):
            # Color JNT yellow
            self.setColor(17)
            self.ColorNumber = 17
        elif (self.side == "L"):
            # Color JNT blue
            self.setColor(6)
            self.ColorNumber =6
        elif (self.side == "R"):
            # Colour JNT red
            self.setColor(13)
            self.ColorNumber = 13


    def getRadius(self):
        ''' radius value'''
        return mc.getAttr(self.name+".radius")
    @property
    def radius(self):
        ''' returns node's plug '''
        return self.getPlug("radius")
    @property
    def jointOrient(self):
        ''' '''
        return self.getPlug("jointOrient")
    @property
    def jointOrientX(self):
        ''' '''
        return self.getPlug("jointOrientX")
    @property
    def jointOrientY(self):
        ''' '''
        return self.getPlug("jointOrientY")
    @property
    def jointOrientZ(self):
        ''' '''
        return self.getPlug("jointOrientZ")
    @property
    def getDawStyleAttr(self):
        return self.name + ".drawStyle"
    
    
class circle(transform):
    elemIndex = 0
    nodeType = "nurbsCurve"
    def setColor(self, colorNumber):
        mc.setAttr(self.name+".overrideEnabled", 1);
        #set color to yellow
        mc.setAttr(self.name+".overrideColor", colorNumber)
    def __init__(self, side="C", name="circle", type="CTL", parent=None): 
        super(circle, self).__init__(side, name+"Shape", type, parent)
        
        self.name = side+"_"+name+"0"+str(self.elemIndex)+"_"+type
        self.transformNode = mc.listRelatives(self.name, p=True)
        self.makeCircle = mc.createNode("makeNurbCircle", n=self.name.replace(name, "makeCircle"+name))
        mc.connectAttr(self.makeCircle+".outputCurve", self.name+".create")
        circle.elemIndex +=1

        # Coloring Circles
        if (self.side == "C"):
            # Color CTL yellow
            self.setColor(17)
            self.ColorNumber = 17
        elif (self.side == "L"):
            # Color CTL blue
            self.setColor(6)
            self.ColorNumber =6
        elif (self.side == "R"):
            # Colour CTL red
            self.setColor(13)
            self.ColorNumber = 13

        # DELETING HISTORY
        mc.delete(self.name, ch=True)


 # NEW SCENE


