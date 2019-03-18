import rigFn as rigFn
import functions as fn
import mayaModule as mmod
import mayaNode as mNode
import maya.cmds as mc



def parentConstraintMO(targetParent, objParent, object, maintainOffset = True, translate=True, rotate=True, scale=True):
    # Matrix Mult
    side = fn.concat_str(str1 = object, s1_begin=0, s1_end=len(object)-1 )
    matrix = mNode.multMatrix(side=side, name="transformationMatrix")
    if (maintainOffset == True):
            
        localOffset = fn.getLocalOffset(targetParent, object)
        mc.setAttr(matrix.name+".matrixIn[0]", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
    
    mmod.connectAttr(targetParent+".worldMatrix", matrix.name+".matrixIn[1]")
    mmod.connectAttr(objParent+".worldInverseMatrix", matrix.name+".matrixIn[2]")
    decomposeMatrix = mNode.decomposeMatrix(side=side, name="transformation")
    mmod.connectAttr(matrix.getMatrixSum(), decomposeMatrix.getInputMatrix())
    if (translate == True):
        mmod.connectAttr(decomposeMatrix.getOutputTranslate(), object+".translate")
    if (rotate == True):
        mmod.connectAttr(decomposeMatrix.getOutputRotate(), object+".rotate")
    if (scale == True):
        mmod.connectAttr(decomposeMatrix.getOutputScale(), object+".scale")
  

parentConstraintMO("R_armIKWrist03_CTL", "R_bindArm00_GRP", "R_hand00_GRP", translate=False, rotate=True, scale=False )