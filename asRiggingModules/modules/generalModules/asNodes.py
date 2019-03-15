import maya.cmds as mc
import mayaNode as node

class asMatloft(node.utilityNode):
    elemIndex = 0
    nodeType = "asMatloft"
    def __init__(self, side="C", name="asMatloft", type ="MLFT"):
        super(asMatloft, self).__init__(self.nodeType, side, name, type)
        asMatloft.elemIndex+=1

    # OUTPUT ATTRIBUTES
    def getOutputSurface(self):
        return self.name+".outputSurface"
    @property
    def outputSurface(self):
        ''' returns node's plug '''
        return self.getPlug("outputSurface")
    @outputSurface.setter
    def outputSurface(self, value):
        mc.setAttr(self.name+".outputSurface", value)

    def getSurfaceLength(self):
        return self.name+".surfaceLength"
    @property
    def surfaceLength(self):
        ''' returns node's plug '''
        return self.getPlug("surfaceLength")
    @surfaceLength.setter
    def surfaceLength(self, value):
        mc.setAttr(self.name+".surfaceLength", value)


class asRivet(node.utilityNode):
    elemIndex = 0
    nodeType = "asRivet"
    def __init__(self, side="C", name="asRivet", type ="RIV"):
        super(asRivet, self).__init__(self.nodeType, side, name, type)
        asRivet.elemIndex+=1

    
    # input ATTRIBUTES
    def getInputSurface(self):
        return self.name+".inputSurface"
    @property
    def inputSurface(self):
        ''' returns node's plug '''
        return self.getPlug("inputSurface")
    @inputSurface.setter
    def inputSurface(self, value):
        mc.setAttr(self.name+".inputSurface", value)
    
    def getParameterU(self):
        return self.name+".parameterU"
    @property
    def parameterU(self):
        ''' returns node's plug '''
        return self.getPlug("parameterU")
    @parameterU.setter
    def parameterU(self, value):
        mc.setAttr(self.name+".parameterU", value)
    
    def getParameterV(self):
        return self.name+".parameterV"
    @property
    def parameterV(self):
        ''' returns node's plug '''
        return self.getPlug("parameterV")
    @parameterV.setter
    def parameterV(self, value):
        mc.setAttr(self.name+".parameterV", value)

    
    def getPercentage(self):
        return self.name+".percentage"
    @property
    def percentage(self):
        ''' returns node's plug '''
        return self.getPlug("percentage")
    @percentage.setter
    def percentage(self, value):
        mc.setAttr(self.name+".percentage", value)


    # OUTPUT ATTRIBUTES

    # output rotation
    
    # output Rotation
    def getOutRotation(self):
        return self.name +".outRotation"
    @property
    def outRotation(self):
        return self.getPlug("outRotation")

    # out Translation
    def getoutTranslation(self):
        return self.name +".outTranslation"
    
    @property
    def outTranslation(self):
        return self.getPlug("outTranslation")


    