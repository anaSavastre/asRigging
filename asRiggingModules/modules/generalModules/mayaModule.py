import maya.cmds as mc
import maya.OpenMaya as om

import functions as fn

def getParent(grp):
    '''
    Returns parent of given transform node in the outliner 
    '''
    return mc.listRelatives(grp, p=True)


def resetJNTCount():
    joint.elemIndex = 0

def resetTRNCount():
    transform.elemIndex = 0

def connectAttr(attr1, attr2):
    mc.connectAttr(attr1, attr2, f=True)

def connectPlugs(plug1, plug2):
    dgModifier = om.MDGModifier()
    dgModifier.connect(plug1, plug2)
    dgModifier.doIt()


def testProject():
    mc.file(new = True, f=True)
    
    side ="C"
    parent = None
    legName="leg"
    legGRP = transform(side=side, name=legName, type="GRP", parent=parent)
    legJntGRP = transform(side=side, name=legName+"Joints", type="GRP", parent=legGRP)
    limitedAnkleGRP = transform(side=side, name=legName+"LimitedAnkle", type="GRP", parent=legGRP)
    ankleCtrl = constructCTL(ankleGuide, side=side, name=legName+"Ankle", parent=legGRP)
    settingsGRP = transform(side=side, name=legName+"Settings", type="GRP", parent=legGRP)



class utilityNode(object):
    elemIndex = 0
    def __init__(self, nodeType, side="C", name="name", type="NOD"):
        self.nodeType = nodeType
        self.side = side
        self.type = type
        self.name = side+"_"+name+"0"+str(self.elemIndex)+"_"+type
        self.utilityNode = mc.createNode(self.nodeType, n=self.name)
    def getPlug(self, nodeName):
        ''' returns node's plug '''
        self_mObject =self.getMObject()
        dependencyNode =om.MFnDependencyNode(self_mObject)
        try:
            plug = dependencyNode.findPlug(nodeName)
            return plug
        except:
            print "plug not returned"
            return None
    
    def getMObject(self):
        selectionList = om.MSelectionList()
        try: 
            selectionList.add(self.name)
            mObj = om.MObject()
            selectionList.getDependNode(0, mObj)
            return mObj
        except:
            print "mObj not returned"
            return None

class multDoubleLinear(utilityNode):
    elemIndex = 0
    nodeType = "multDoubleLinear"
    def __init__(self, side="C", name="multDoubleLinear", type ="MTL"):
        super(multDoubleLinear, self).__init__(self.nodeType, side, name, type)
        multDoubleLinear.elemIndex+=1

    # INPUT ATTRIBUTES
    def getInput1(self):
            return self.name+".input1"
    @property
    def input1(self):
        ''' returns node's plug '''
        return self.getPlug("input1")
    @input1.setter
    def input1(self, value):
        mc.setAttr(self.name+".input1", value)

    def getInput2(self):
        return self.name+".input2"
    @property
    def input2(self):
        ''' returns node's plug '''
        return self.getPlug("input2")
    @input1.setter
    def input2(self, value):
        mc.setAttr(self.name+".input2", value)
    
    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)

class multiplyDivide(utilityNode):
    ''' JUST OPERATION ATTR IMPLEMENTED
    needs refinement'''
    elemIndex = 0
    nodeType = "multiplyDivide"
    def __init__(self, side="C", name="multiplyDivide", type ="MDV"):
        super(multiplyDivide, self).__init__(self.nodeType, side, name, type)
        multiplyDivide.elemIndex+=1
    # INPUT ATTRIBUTES
    # Operation
    def getOperation(self):
        return self.name+".operation"
    @property
    def operation(self):
        ''' returns node's plug '''
        return self.getPlug("operation")
    @operation.setter
    def operation(self, value):
        mc.setAttr(self.name+".operation", value)
   
    # Input1
    def getInput1(self):
        return self.name+".input1"
    @property
    def input1(self):
        ''' returns node's plug '''
        return self.getPlug("input1")
    @input1.setter
    def input1(self, value):
        mc.setAttr(self.name+".input1", value)

    # Input2
    def getInput2(self):
        return self.name+".input2"
    @property
    def input2(self):
        ''' returns node's plug '''
        return self.getPlug("input2")
    @input2.setter
    def input2(self, value):
        mc.setAttr(self.name+".input2", value)

    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)
     
class blendColors(utilityNode):
    elemIndex = 0
    nodeType = "blendColors"
    def __init__(self, side="C", name="blendColors", type ="BLD"):
        super(blendColors, self).__init__(self.nodeType, side, name, type)
        blendColors.elemIndex+=1

    # INPUT ATTRIBUTES
    # Color1
    def getColor1(self):
        return self.name+".color1"
    @property
    def color1(self):
        ''' returns node's plug '''
        return self.getPlug("color1")
    @color1.setter
    def color1(self, value):
        mc.setAttr(self.name+".color1", value)

    # Color2
    def getColor2(self):
        return self.name+".color2"
    @property
    def color2(self):
        ''' returns node's plug '''
        return self.getPlug("color2")
    @color2.setter
    def color2(self, value):
        mc.setAttr(self.name+".color2", value)

    # Blender
    def getBlender(self):
        return self.name+".blender"
    @property
    def blender(self):
        ''' returns node's plug '''
        return self.getPlug("blender")
    @blender.setter
    def blender(self, value):
        mc.setAttr(self.name+".blender", value)

    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)  


class vectorProduct(utilityNode):
    ''' not completely implemented'''
    elemIndex = 0
    nodeType = "vectorProduct"
    def __init__(self, side="C", name="vectorProduct", type ="VEC"):
        super(vectorProduct, self).__init__(self.nodeType, side, name, type)
        vectorProduct.elemIndex+=1
    
    # INPUT ATTRIBUTES
    # Operation
    def getOperation(self):
        return self.name+".operation"
    @property
    def operation(self):
        ''' returns node's plug '''
        return self.getPlug("operation")
    @operation.setter
    def operation(self, value):
        mc.setAttr(self.name+".operation", value)

    # normalizeOutput
    def getnormalizeOutput(self):
        return self.name+".normalizeOutput"
    @property
    def normalizeOutput(self):
        ''' returns node's plug '''
        return self.getPlug("normalizeOutput")
    @normalizeOutput.setter
    def normalizeOutput(self, value):
        mc.setAttr(self.name+".normalizeOutput", value)

    # input1
    def getInput1(self):
        return self.name+".input1"
    @property
    def input1(self):
        ''' returns node's plug '''
        return self.getPlug("input1")
    @input1.setter
    def input1(self, value):
        mc.setAttr(self.name+".input1", value)
    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)
     


class clamp(utilityNode): 
    ''' not completely implemented'''
    elemIndex = 0
    nodeType = "clamp"
    def __init__(self, side="C", name="clamp", type ="CLP"):
        super(clamp, self).__init__(self.nodeType, side, name, type)
        clamp.elemIndex+=1
    
    # INPUT ATTRIBUTES
    # Input
    def getInput(self):
        return self.name+".input"
    @property
    def input(self):
        ''' returns node's plug '''
        return self.getPlug("input")
    @input.setter
    def input(self, value):
        mc.setAttr(self.name+".input", value)

    # InputR
    def getInputR(self):
        return self.name+".input.inputR"
    @property
    def inputR(self):
        ''' returns node's plug '''
        return self.getPlug("inputR")
    @inputR.setter
    def inputR(self, value):
        mc.setAttr(self.name+".input.inputR", value)

    # inputG
    def getinputG(self):
        return self.name+".input.inputG"
    @property
    def inputG(self):
        ''' returns node's plug '''
        return self.getPlug("inputG")
    @inputG.setter
    def inputG(self, value):
        mc.setAttr(self.name+".input.inputG", value)

    # inputB
    def getinputB(self):
        return self.name+".input.inputB"
    @property
    def inputB(self):
        ''' returns node's plug '''
        return self.getPlug("inputB")
    @inputB.setter
    def inputB(self, value):
        mc.setAttr(self.name+".input.inputB", value)

    # Min
    def getMin(self):
        return self.name+".min"
    @property
    def min(self):
        ''' returns node's plug '''
        return self.getPlug("min")
    @min.setter
    def min(self, value):
        mc.setAttr(self.name+".min", value)

    # Max
    def getMax(self):
        return self.name+".max"
    @property
    def max(self):
        ''' returns node's plug '''
        return self.getPlug("max")
    @max.setter
    def max(self, value):
        mc.setAttr(self.name+".max", value)

    # maxR
    def getMaxR(self):
        return self.name+".maxR"
    @property
    def maxR(self):
        ''' returns node's plug '''
        return self.getPlug("maxR")
    @maxR.setter
    def maxR(self, value):
        mc.setAttr(self.name+".maxR", value)

    # OUTPUT ATTRIBUTES
    # outputR
    def getOutputR(self):
        return self.name+".outputR"
    @property
    def outputR(self):
        ''' returns node's plug '''
        return self.getPlug("outputR")
    @outputR.setter
    def outputR(self, value):
        mc.setAttr(self.name+".outputR", value)


class plusMinusAverage(utilityNode):
    ''' JUST OPERATION ATTR IMPLEMENTED
    needs refinement'''
    elemIndex = 0
    nodeType = "plusMinusAverage"
    def __init__(self, side="C", name="plusMinusAverage", type ="PMA"):
        super(plusMinusAverage, self).__init__(self.nodeType, side, name, type)
        plusMinusAverage.elemIndex+=1
    # INPUT ATTRIBUTES
    def getOperation(self):
        return self.name+".operation"
    @property
    def operation(self):
        ''' returns node's plug '''
        return self.getPlug("operation")
    @operation.setter
    def operation(self, value):
        mc.setAttr(self.name+".operation", value)
 
    # OUTPUT ATTRIBUTES
    def getOutput3D(self):
        return self.name+".output3D"
    @property
    def output3D(self):
        ''' returns node's plug '''
        return self.getPlug("output3D")
    @output3D.setter
    def output3D(self, value):
        mc.setAttr(self.name+".output3D", value)


class angleBetween(utilityNode):
    elemIndex = 0
    nodeType = "angleBetween"
    def __init__(self, side="C", name="angleBetween", type ="ANG"):
        super(angleBetween, self).__init__(self.nodeType, side, name, type)
        angleBetween.elemIndex+=1
    # INPUT ATTRIBUTES
    def getVector1(self):
        return self.name+".vector1"
    @property
    def vector1(self):
        ''' returns node's plug '''
        return self.getPlug("vector1")
    @vector1.setter
    def vector1(self, value):
        mc.setAttr(self.name+".vector1", value)

    def getVector2(self):
        return self.name+".vector2"
    @property
    def vector2(self):
        ''' returns node's plug '''
        return self.getPlug("vector2")
    @vector1.setter
    def vector2(self, value):
        mc.setAttr(self.name+".vector2", value)
    # OUTPUT ATTRIBUTES
    def getEuler(self):
        return self.name+".euler"
    @property
    def euler(self):
        ''' returns node's plug '''
        return self.getPlug("euler")
    @euler.setter
    def euler(self, value):
        mc.setAttr(self.name+".euler", value)

class animBlendNodeAdditiveDA(utilityNode):
    elemIndex = 0
    nodeType = "animBlendNodeAdditiveDA"
    def __init__(self, side="C", name="animBlendNodeAdditiveDA", type ="AddDA"):
        super(animBlendNodeAdditiveDA, self).__init__(self.nodeType, side, name, type)
        animBlendNodeAdditiveDA.elemIndex+=1
    # inputA
    def getInputA(self):
        return self.name+".inputA"
    @property
    def inputA(self):
        ''' returns node's plug '''
        return self.getPlug("inputA")
    @inputA.setter
    def inputA(self, value):
        mc.setAttr(self.name+".inputA", value)
    # inputB
    def getInputB(self):
        return self.name+".inputB"
    @property
    def inputB(self):
        ''' returns node's plug '''
        return self.getPlug("inputB")
    @inputB.setter
    def inputB(self, value):
        mc.setAttr(self.name+".inputB", value)
    def getInputA(self):
        return self.name+".inputA"
    # weightA
    def getWeightA(self):
        return self.name+".weightA"
    @property
    def weightA(self):
        ''' returns node's plug '''
        return self.getPlug("weightA")
    @weightA.setter
    def weightA(self, value):
        mc.setAttr(self.name+".weightA", value)
    # weightB
    def getWeightB(self):
        return self.name+".weightB"
    @property
    def weightB(self):
        ''' returns node's plug '''
        return self.getPlug("weightB")
    @weightB.setter
    def weightB(self, value):
        mc.setAttr(self.name+".weightB", value)
    
    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)
    


class condition(utilityNode):
    elemIndex = 0
    nodeType = "condition"
    def __init__(self, side="C", name="condition", type ="CND"):
        super(condition, self).__init__(self.nodeType, side, name, type)
        condition.elemIndex+=1
    # INPUT ATTRIBUTES
    def getOperation(self):
        return self.name+".operation"
    @property
    def operation(self):
        ''' returns node's plug '''
        return self.getPlug("operation")
    @operation.setter
    def operation(self, value):
        mc.setAttr(self.name+".operation", value)
 
    def getFirstTerm(self):
        return self.name+".firstTerm"
    @property
    def firstTerm(self):
        ''' returns node's plug '''
        return self.getPlug("firstTerm")
    @firstTerm.setter
    def firstTerm(self, value):
        mc.setAttr(self.name+".firstTerm", value)
    
    # INPUT ATTRIBUTES
    def getColorIfFalse(self):
        return self.name+".colorIfFalse"
    @property
    def colorIfFalse(self):
        ''' returns node's plug '''
        return self.getPlug("colorIfFalse")
    @colorIfFalse.setter
    def colorIfFalse(self, value):
        mc.setAttr(self.name+".colorIfFalse", value)
    
    def getColorIfTrue(self):
        return self.name+".colorIfTrue"
    @property
    def colorIfTrue(self):
        ''' returns node's plug '''
        return self.getPlug("colorIfTrue")
    @colorIfTrue.setter
    def colorIfTrue(self, value):
        mc.setAttr(self.name+".colorIfTrue", value)

    # OUTPUT ATTRIBUTES
    def getOutColor(self):
        return self.name+".outColor"
    @property
    def outColor(self):
        ''' returns node's plug '''
        return self.getPlug("outColor")
    @outColor.setter
    def outColor(self, value):
        mc.setAttr(self.name+".outColor", value)
        

    


class decomposeMatrix(utilityNode):
    elemIndex = 0
    nodeType = "decomposeMatrix"
    def __init__(self, side="C", name="decomposeMatrix", type ="DMTX"):
        super(decomposeMatrix, self).__init__(self.nodeType, side, name, type)
        decomposeMatrix.elemIndex+=1

    # INPUT ATTRIBUTES
    # inputMatrix
    def getInputMatrix(self):
        return self.name+".inputMatrix"
    @property
    def inputMatrix(self):
        ''' returns attr str'''
        return self.getPlug("inputMatrix")
    @inputMatrix.setter
    def inputMatrix(self, value):
        mc.setAttr(self.name+".inputMatrix", value)

    # OUTPUT ATTRIBUTES
    # output Quat
    @property
    def outputQuat(self):
        return self.name +".outputQuat"

    # output Rotate
    @property
    def outputRotate(self):
        return self.getPlug("outputRotate")

    # output Translate
    def getOutputTranslate(self):
        return self.name +".outputTranslate"
    
    @property
    def outputTranslate(self):
        return self.getPlug("outputTranslate")

    # output Scale
    @property
    def outputScale(self):
        return self.getPlug("outputScale")

 
class distanceBetween(utilityNode):
    elemIndex = 0
    nodeType = "distanceBetween"
    def __init__(self, side="C", name="distanceBetween", type ="DST"):
        super(distanceBetween, self).__init__(self.nodeType, side, name, type)
        distanceBetween.elemIndex+=1

    # INPUT ATTRIBUTES
    # inMatrix1
    @property
    def inMatrix1(self):
        ''' returns node's plug '''
        return self.getPlug("inMatrix1")
    @inMatrix1.setter
    def inMatrix1(self, value):
        mc.setAttr(self.name+".inMatrix1", value)

     # inMatrix2
    def getInMatrix2(self):
        return self.name+".inMatrix2"
    @property
    def inMatrix2(self):
        ''' returns attr str'''
        return self.getPlug("inMatrix2")
    @inMatrix2.setter
    def inMatrix2(self, value):
        mc.setAttr(self.name+".inMatrix2", value)

    # OUTPUT ATTRIBUTES
    def getDistance(self):
        ''' return attr str'''
        return self.name+".distance"
    @property
    def distance(self):
        ''' returns attr plug'''
        return self.getPlug("distance")
class multDoubleLinear(utilityNode):
    elemIndex = 0
    nodeType = "multDoubleLinear"
    def __init__(self, side="C", name="multDoubleLinear", type ="MTL"):
        super(multDoubleLinear, self).__init__(self.nodeType, side, name, type)
        multDoubleLinear.elemIndex+=1

    # INPUT ATTRIBUTES
    def getInput1(self):
            return self.name+".input1"
    @property
    def input1(self):
        ''' returns node's plug '''
        return self.getPlug("input1")
    @input1.setter
    def input1(self, value):
        mc.setAttr(self.name+".input1", value)

    def getInput2(self):
        return self.name+".input2"
    @property
    def input2(self):
        ''' returns node's plug '''
        return self.getPlug("input2")
    @input1.setter
    def input2(self, value):
        mc.setAttr(self.name+".input2", value)
    
    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)

class addDoubleLinear(utilityNode):
    elemIndex = 0
    nodeType = "addDoubleLinear"
    def __init__(self, side="C", name="addDoubleLinear", type ="ADD"):
        super(addDoubleLinear, self).__init__(self.nodeType, side, name, type)
        addDoubleLinear.elemIndex+=1

    # INPUT ATTRIBUTES
    def getInput1(self):
            return self.name+".input1"
    @property
    def input1(self):
        ''' returns node's plug '''
        return self.getPlug("input1")
    @input1.setter
    def input1(self, value):
        mc.setAttr(self.name+".input1", value)

    def getInput2(self):
        return self.name+".input2"
    @property
    def input2(self):
        ''' returns node's plug '''
        return self.getPlug("input2")
    @input1.setter
    def input2(self, value):
        mc.setAttr(self.name+".input2", value)
    
    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)
    

class transform(object):

    elemIndex = 0
    nodeType = "transform"
    # visibility = 1
    # Main attributes
    def __init__(self, side="C", name="name", type="TRF", parent=None): 
        self.side = side
        self.type = type
        self.name = side+"_"+name+"0"+str(self.elemIndex)+"_"+type
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
    # rotateX
    @property
    def rotateX(self):
        ''' returns node's plug '''
        return self.getPlug("rotateX")
    @rotateX.setter
    def rotateX(self, value):
        mc.setAttr(self.name+".rotateX", value)
    
    def getrotateX(self):
        return mc.getAttr(self.name+".rotateX")

    # rotateY
    @property
    def rotateY(self):
        ''' returns node's plug '''
        return self.getPlug("rotateY")
    @rotateY.setter
    def rotateY(self, value):
        mc.setAttr(self.name+".rotateY", value)
    
    def getrotateY(self):
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
        makeCircle = mc.createNode("makeNurbCircle", n=self.name.replace(name, "makeCircle"+name))
        mc.connectAttr(makeCircle+".outputCurve", self.name+".create")
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
   
        
