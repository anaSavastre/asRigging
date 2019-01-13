import maya.cmds as mc
import maya.mel as mel

import mayaModule as mmod
import mayaNode as mNode

mc.file(new = True, f=True)


def skinSlidingSetup ():
    mc.file( "D:/Bournemouth University/CVA_Y3/asSkinSliding/dinoRig01.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)
    # nianBody = "Geometry|Body"
    # mc.deformer(nianBody, type="asSkinSliding")
    # # mc.makePaintable("weightGeometryFilter", "weights", attrType="multiFloat", sm="deformer")
    # # melCmd = 'AbcImport -mode import "D:/Bournemouth University/CVA_Y3/exportAlembic/squerrelAnim .abc";'
    # # mel.eval(melCmd)
        
    # nianBody = "C_SpinosaurusBody_L0_PLY"
    # deformer  = mc.deformer(nianBody, type="asSlidingSkinning")[0]
    # position = mc.xform(nianBody+".vtx[6182]", ws=True, q=True, t=True)
    # grp = mmod.transform()
    
    # mc.xform(grp.name, t=position, ws=True)
    # loc = mmod.locator(parent=grp)

    # # TEMPORARY DECOMPOSE MATRIX
    # decompMatrix = mNode.decomposeMatrix()
    # mmod.connectAttr(loc.name+".worldMatrix[0]", decompMatrix.getInputMatrix())
    # # mmod.connectAttr(decompMatrix.getOutputTranslate(), deformer+".translate")
    # mmod.connectAttr(loc.name+".translate", deformer+".translate")

    # mc.setAttr(deformer+".vertexId", 6182)


    # nianBody = "C_SpinosaurusBody_L0_PLY"
    # deformer  = mc.deformer(nianBody, type="asSlidingSkinning")[0]
    # position = mc.xform(nianBody+".vtx[4925]", ws=True, q=True, t=True)
    # grp = mmod.transform()
    
    # mc.xform(grp.name, t=position, ws=True)
    # loc = mmod.locator(parent=grp)

    # # TEMPORARY DECOMPOSE MATRIX
    # decompMatrix = mNode.decomposeMatrix()
    # mmod.connectAttr(loc.name+".worldMatrix[0]", decompMatrix.getInputMatrix())
    # # mmod.connectAttr(decompMatrix.getOutputTranslate(), deformer+".translate")
    # mmod.connectAttr(loc.name+".translate", deformer+".translate")

    # mc.setAttr(deformer+".vertexId", 4925)


skinSlidingSetup()

