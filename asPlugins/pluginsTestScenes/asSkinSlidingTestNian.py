import maya.cmds as mc
import maya.mel as mel

import mayaModule as mmod
import mayaNode as mNode

mc.file(new = True, f=True)


def skinSlidingSetup ():
    mc.file( "D:/Bournemouth University/CVA_Y3/asSkinSliding/nianRig00.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)
    nianBody = "Geometry|Body"

    deformer  = mc.deformer(nianBody, type="asSurfaceSliding")[0]
    position = mc.xform(nianBody+".vtx[997]", ws=True, q=True, t=True)
    grp = mmod.transform()
    
    mc.xform(grp.name, t=position, ws=True)
    loc = mmod.locator(parent=grp)

    # TEMPORARY DECOMPOSE MATRIX
    decompMatrix = mNode.decomposeMatrix()
    mmod.connectAttr(loc.name+".worldMatrix[0]", decompMatrix.getInputMatrix())
    # mmod.connectAttr(decompMatrix.getOutputTranslate(), deformer+".translate")
    mmod.connectAttr(loc.name+".translate", deformer+".translate")

    mc.setAttr(deformer+".vertexId", 997)
skinSlidingSetup()