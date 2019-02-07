''' 
Ana Maria Savastre
Bournemouth University 

'''
import maya.cmds as mc
import maya.OpenMaya as om
import maya.OpenMayaMPx as omMPx
import sys


nodeName = "asAnimationRetargeting"
nodeId = om.MTypeId(0xBA00104)

class asAnimationRetargeting(omMPx.MPxNode):
    '''
    Animation Retargeting Node
    '''
    
    # # Default maya class attributes
    # kPluginNodeId = om.MTypeId(0xBA00104)
    # kPluginNodeName = "asAnimationRetargeting"


    # Custom inputs
    as_targetParentWorldMatrix = om.MObject()
    as_objectParentWorldInverseMatrix = om.MObject()

    as_outRotateX = om.MObject()
    as_outRotateY = om.MObject()
    as_outRotateZ = om.MObject()
    
    as_outTranslateX = om.MObject()
    as_outTranslateY = om.MObject()
    as_outTranslateZ = om.MObject()
    as_outRotate = om.MObject()
    as_outTranslate = om.MObject()
    
    def __init__(self):
        omMPx.MPxNode.__init__(self)
    def compute(self, pPlug, pDataBlock):
        '''
        
        '''
        print "compute 00"
        if (pPlug == asAnimationRetargeting.as_outRotateX or pPlug == asAnimationRetargeting.as_outRotateY or pPlug == asAnimationRetargeting.as_outRotateZ or pPlug == asAnimationRetargeting.as_outTranslateX or pPlug == asAnimationRetargeting.as_outTranslateY or pPlug == asAnimationRetargeting.as_outTranslateZ):  
            print "compute"
            # dataHandleRadius = dataBlock.inputValue(WheelNode.inRadius)
            # dataHandleTranslate = dataBlock.inputValue(WheelNode.inTranslate)
            inParentWorldMatrix = pDataBlock.inputValue(asAnimationRetargeting.as_targetParentWorldMatrix).asMatrix()
            inParentInverseMatrix = pDataBlock.inputValue(asAnimationRetargeting.as_objectParentWorldInverseMatrix).asMatrix()
            transformationMatrix = om.MTransformationMatrix()
            transformationMatrix *= inParentInverseMatrix * inParentWorldMatrix

            eulerRotation = transformationMatrix.eulerRotation();

            
            # OUTPUT 
            # //Translation Handle
            outTranslationHandle = pDataBlock.outputValue(asAnimationRetargeting.as_outTranslate);
            outTranslationHandle.setMVector(transformMatrix.getTranslation(om.MSpace.kWorld)+om.MVector(nrbS_point));
            outTranslationHandle.setClean();

            dataHandleRotate = pDataBlock.outputValue(asAnimationRetargeting.as_outRotate)
            dataHandleRotate.set3Double(eulerRotation.x, eulerRotation.y, eulerRotation.z)
            pDataBlock.setClean(pPlug)
            
        else:
            return om.kUnknownParameter



   
			
def nodeCreator():
    return omMPx.asMPxPtr( asAnimationRetargeting())
	
def nodeInitializer():
    #  1. creating a function set for numeric attributes
    matrixAttrFn = om.MFnMatrixAttribute()
    numericAttrFn = om.MFnNumericAttribute()
    compoundAttrFn = om.MFnCompoundAttribute ()

    # 2. create the attributes
    # PARENT WORLD MATRIX
    asAnimationRetargeting.as_targetParentWorldMatrix = matrixAttrFn.create("parentWM", "parentWM", om.MFnMatrixAttribute.kDouble)
    matrixAttrFn.setReadable(1)
    matrixAttrFn.setWritable(1)
    matrixAttrFn.setStorable(1)
    matrixAttrFn.setKeyable(1)
    asAnimationRetargeting.addAttribute(asAnimationRetargeting.as_targetParentWorldMatrix)

    # PARENT INVERSE MATRIX
    asAnimationRetargeting.as_objectParentWorldInverseMatrix = matrixAttrFn.create("parentInverseMatrix","pInvM",om.MFnMatrixAttribute.kDouble)
    matrixAttrFn.setReadable(1)
    matrixAttrFn.setWritable(1)
    matrixAttrFn.setStorable(1)
    matrixAttrFn.setKeyable(1)	
    asAnimationRetargeting.addAttribute(asAnimationRetargeting.as_objectParentWorldInverseMatrix)

    # OUTPUT ROTATE
    # asAnimationRetargeting.as_outRotateX = numericAttrFn.create("outputRotateX","outRotX",om.MFnNumericData.kDouble, 0.0)
    # numericAttrFn.setKeyable(1)
    # asAnimationRetargeting.as_outRotateY = numericAttrFn.create("outputRotateY","outRotY",om.MFnNumericData.kDouble, 0.0)
    # numericAttrFn.setKeyable(1)
    # asAnimationRetargeting.as_outRotateZ = numericAttrFn.create("outputRotateZ","outRotZ",om.MFnNumericData.kDouble, 0.0)
    # numericAttrFn.setKeyable(1)
    asAnimationRetargeting.as_outRotate = compoundAttrFn.create("outputRotate","outRot")
    compoundAttrFn.setReadable(1)
    compoundAttrFn.setWritable(1)
    compoundAttrFn.setStorable(1)
    compoundAttrFn.setKeyable(1)
    compoundAttrFn.addChild(asAnimationRetargeting.as_outRotateX)
    compoundAttrFn.addChild(asAnimationRetargeting.as_outRotateY)    
    compoundAttrFn.addChild(asAnimationRetargeting.as_outRotateZ)	
    asAnimationRetargeting.addAttribute(asAnimationRetargeting.as_outRotate)

    # OUTPUT TRANSLATE
    asAnimationRetargeting.as_outTranslateX = numericAttrFn.create("outputTranslateX","outTransX",om.MFnNumericData.kDouble, 0.0)
    numericAttrFn.setKeyable(1)
    asAnimationRetargeting.as_outTranslateY = numericAttrFn.create("outputTranslateY","outTransY",om.MFnNumericData.kDouble, 0.0)
    numericAttrFn.setKeyable(1)
    asAnimationRetargeting.as_outTranslateZ = numericAttrFn.create("outputTranslateZ","outTransZ",om.MFnNumericData.kDouble, 0.0)
    numericAttrFn.setKeyable(1)
    asAnimationRetargeting.as_outTranslate = numericAttrFn.create("outputTranslate","outTrans", asAnimationRetargeting.as_outTranslateX, asAnimationRetargeting.as_outTranslateY, asAnimationRetargeting.as_outTranslateZ)
    numericAttrFn.setReadable(1)
    numericAttrFn.setWritable(1)
    numericAttrFn.setStorable(1)
    numericAttrFn.setKeyable(1)	
    asAnimationRetargeting.addAttribute(asAnimationRetargeting.as_outTranslate)	

    # 4. Attribute Affects
    asAnimationRetargeting.attributeAffects(asAnimationRetargeting.as_targetParentWorldMatrix, asAnimationRetargeting.as_outRotate)
    asAnimationRetargeting.attributeAffects(asAnimationRetargeting.as_targetParentWorldMatrix, asAnimationRetargeting.as_outTranslate)

    asAnimationRetargeting.attributeAffects(asAnimationRetargeting.as_objectParentWorldInverseMatrix, asAnimationRetargeting.as_outRotate)
    asAnimationRetargeting.attributeAffects(asAnimationRetargeting.as_objectParentWorldInverseMatrix, asAnimationRetargeting.as_outTranslate)


def initializePlugin(mobject):
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.registerNode(nodeName, nodeId, nodeCreator, nodeInitializer )
    except:
        sys.stderr.write( "Failed to register command: %s\n" % nodeName )

# Uninitialize the script plug-in
def uninitializePlugin(mobject):
    mplugin = omMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( nodeName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % nodeName )
	
	
	
	
	
	
