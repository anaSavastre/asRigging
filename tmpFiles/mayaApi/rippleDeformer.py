import sys
import maya.OpenMaya as om
import maya.OpenMayaMPx as omMpx

nodeName= "asRipple"

nodeID = om.MTypeId(0x102fff)


class ripple(omMpx.MPxDeformerNode):
    ''' 
    commands ------> MPxCommand
    Custom Node----->MPxNode
    Deformenr------->MPxDEformerNode
    '''
    mObj_amplitude = om.MObject()
    mObj_displace = om.MObject()
    def __init__(self):
        omMpx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIterator, matrix, geometryIndex):
        input = omMpx.cvar.MPxDeformerNode_input
        # 1.Attach a handle to input Array Attribute
        dataHandleInputArray = dataBlock.inputArrayValue(input)
        # 2.Jump to curren telement
        dataHandleInputArray.jumpToElement(geometryIndex)
        # 3.Attach a handle to specific data block
        dataHandleInputElement = dataHandleInputArray.inputValue()
        # 4.Reach to the child - inputGEom

        inputGeom = omMpx.cvar.MPxDeformerNode_inputGEom
        dataHandleInputGEom = dataHandleInputElement.child(inputGeom)
        inMesh = dataHandleInputGeom.asMesh()

        envelope = omMpx.cvar.MPxDeformerNode_envelope
        dataHandleEnvelope = 


def deformerCreator():
    nodePtr = omMpx.asMPxPtr(ripple())
    return nodePtr

def nodeInitializer():
    ''' 
    Create Attribute
    Attach Attribute 
    Design Circuitry
    '''

    mFnAttr = om.MFnNumericAttribute()
    ripple.mObj_amplitude = mFnAttr.create("attributeValue", "attrVal", om.MFnNumericData.kFloat, 0.0)
    # mFnAttr.keyable(1)
    mFnAttr.setMin(0.0)
    mFnAttr.setMax(1.0)

    ripple.mObj_displace = mFnAttr.create("displaceValue", "dispVal", )
    mFnAttr.setMin(0.0)
    mFnAttr.setMax(10.0)

    # Add Attributes
    ripple.addAttribute(ripple.mObj_amplitude)
    ripple.addAttribute(ripple.mObj_displace)

    '''
    SWIG - simplify wrapper interface generator

    '''
    outputGeom = omMpx.cvar.MPxDeformerNode_outputGeom
    ripple.attributeAffects(ripple.mObj_amplitude, outputGeom)
    ripple.attributeAffects(ripple.mObj_displace, outputGeom)

def initializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject, "Ana Savastre", "1.0")
    try:
        mplugin.registerNode(nodeName, nodeID, deformerCreator, nodeInitializer, omMpx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write("Failed to register node: %s" % nodeName)
        raise
    
def uninitializePlugin(mobject):
    mplugin = omMpx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(mobject)
    except:
        sys.stderr.write("Failed to deregister node: %s" % nodeName)
        raise