import maya.cmds as mc
import maya.OpenMaya as om

import functions as fn


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

class multMatrix(utilityNode):
    elemIndex = 0
    nodeType = "multMatrix"
    def __init__(self, side="C", name="multMatrix", type ="MatMult"):
        super(multMatrix, self).__init__(self.nodeType, side, name, type)
        multMatrix.elemIndex+=1
    # OUTPUT ATTRIBUTES
    def getMatrixSum(self):
        return self.name+".matrixSum"
    @property
    def matrixSum(self):
        ''' returns node's plug '''
        return self.getPlug("matrixSum")
    @matrixSum.setter
    def matrixSum(self, value):
        mc.setAttr(self.name+".matrixSum", value)
    

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

    def getOutputRotate(self):
        return self.name +".outputRotate"

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
    def getOutputScale(self):
        return self.name +".outputScale"

 
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
    
