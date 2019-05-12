import maya.cmds as mc
import functions as fn
import mayaModule as mmod
import mayaNode as mNode
import controlFn as ctlFn




def createJoint ():

    boundingBox = fn.getBoundingBox()
    center = boundingBox.center()
    
    mc.select (clear= True)
    jnt = mc.joint (p=[center.x, center.y, center.z])
 

def createConnectionGroup (object, name="objectParent", side="C"):
    parentGroup = mmod.transform(side=side, name=name, type="GRP", parent = object)
    mc.parent(parentGroup, fn.getParent(object))
    mc.parent (object, parentGroup)

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
  

def parentConstraint(targetParent, objParent, object):
    # Matrix Mult
    side = fn.concat_str(str1 = object, s1_begin=0, s1_end=len(object)-1 )
    matrix = mNode.multMatrix(side=side, name="transformationMatrix")
    
    mmod.connectAttr(targetParent+".worldMatrix", matrix.name+".matrixIn[0]")
    mmod.connectAttr(objParent+".worldInverseMatrix", matrix.name+".matrixIn[1]")
    decomposeMatrix = mNode.decomposeMatrix(side=side, name="transformation")
    mmod.connectAttr(matrix.getMatrixSum(), decomposeMatrix.getInputMatrix())
    mmod.connectAttr(decomposeMatrix.getOutputTranslate(), object+".translate")
    mmod.connectAttr(decomposeMatrix.getOutputRotate(), object+".rotate")
    mmod.connectAttr(decomposeMatrix.getOutputScale(), object+".scale")

    
def constructJNT(guideJNT, side="C", name="name", parent=None):
    '''
    Function that creates the following hierarchy 
    mmod.transformNode_GRP
        mmod.transformNode_OFS : aligned with guideJNT
            JNT_obj 
    '''
   

    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(guideJNT, ofs)

    # Creating JNT
    jnt = mmod.joint(side=side, name=name, parent=ofs)

    return jnt

def jntHierarchy (guideJnt, side="C", name="name", segmentList=[], parent=None):
    ''' 
        ParentGRP>
                for each elem in the jntList
                    OFS>JNT
    '''
    
    
   

    jntChainList=[]
    # Creating JNT
    root = parent
    for i, jnt in enumerate(guideJnt):
        if (len(segmentList)==len(guideJnt)):
            # NewJnt
            newJnt = mmod.joint(side=side, name=name+segmentList[i], parent=None)
            fn.align(jnt, newJnt)
            jntChainList.append(newJnt)
            mc.makeIdentity(newJnt)
            if root!=None:
                mc.parent(newJnt, root)
            root = newJnt
        else:
            newJnt = mmod.joint(side=side, name=name, parent=None)
            fn.align(jnt, newJnt)
            jntChainList.append(newJnt)
            mc.makeIdentity(newJnt)
            if root!=None:
                mc.parent(newJnt, root)
            root = newJnt
    # for  jnt in jntChainList:
    mc.joint(jntChainList[0].name, oj="xyz", sao="yup", ch=True, e=True)
    mc.setAttr(jntChainList[len(jntChainList)-1].name+".jointOrientX", 0)
    mc.setAttr(jntChainList[len(jntChainList)-1].name+".jointOrientY", 0)
    mc.setAttr(jntChainList[len(jntChainList)-1].name+".jointOrientZ", 0)
    return jntChainList

def createJntChain(jntList, side="C", name="name", segmentList=[], parent=None):
    ''' 
        ParentGRP>
                for each elem in the jntList
                    OFS>JNT
    '''
   

    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
   
    jntChainList=[]
    # Creating JNT
    root = grp
    for i, jnt in enumerate(jntList):
        if (len(segmentList)==len(jntList)):
            ofs = mmod.transform(side=side, name=name+segmentList[i], type="OFS", parent=root)
            # Matching orientation GUIDE > OFS
            fn.align(jnt, ofs)
            # NewJnt
            newJnt = mmod.joint(side=side, name=name+segmentList[i], parent=ofs)
            jntChainList.append(newJnt)
            root = newJnt
        else:
            ofs = mmod.transform(side=side, name=name, type="OFS", parent=root)
            # Matching orientation GUIDE > OFS
            fn.align(jnt, ofs)
            # NewJnt
            newJnt = mmod.joint(side=side, name=name, parent=ofs)
            jntChainList.append(newJnt)
            root = newJnt
    return jntChainList

def constructCTL(guideJNT, side="C", name="name", parent=None, ctrlScale=1, ctrlShape=0):
    '''

    ctrlShape - 0 -> circle
                1 -> box
                2 -> diamond 
                3 -> locator
                4 -> settings
                5 -> square
                6 -> sphere
    Function that creates the following hierarchy 
    mmod.transformNode_GRP
        mmod.transformNode_OFS : aligned with guideJNT
            circle_CTL
                JNT_obj 
    '''
   

    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(guideJNT, ofs)

    # Creating CTL
    if (ctrlShape == 1):
        ctl = ctlFn.boxControl(side=side, name=name, parent=ofs)
    elif (ctrlShape == 2):
        ctl = ctlFn.diamondControl(side=side, name=name, parent=ofs)
    elif (ctrlShape == 3):
        ctl = ctlFn.locatorControl(side=side, name=name, parent=ofs)
    elif (ctrlShape == 4):
        ctl = ctlFn.settingCtl(side=side, name=name, parent=ofs)   
    elif (ctrlShape == 5):
        ctl = ctlFn.squareControl(side = side, name=name, parent=ofs)
    elif (ctrlShape == 6):
        ctl = ctlFn.sphereControl(side = side, name=name, parent=ofs)
    else:
        ctl = mmod.circle(side=side, name=name, parent=ofs)
    # Scaling Ctrl
    try:
        
        
        if (len(fn.getChildren(ctl.name))>1):
            for shape in fn.getChildren(ctl.name):
                fn.scaleShapePoints(shape, mc.getAttr(guideJNT+".radius")/2)
                fn.rotateShapePoints(shape, rotationVector=[0, 90, 0], pivot=mc.xform(guideJNT, q=True, ws=True, t=True))

        else:
            fn.scaleShapePoints(ctl.name, mc.getAttr(guideJNT+".radius")/2)
            fn.rotateShapePoints(ctl.name, rotationVector=[0, 90, 0], pivot=mc.xform(guideJNT, q=True, ws=True, t=True))
    except:
        # Scaling Ctrl
        fn.scaleShapePoints(ctl.name, ctrlScale)
        
        

    # Creating JNT
    jnt = mmod.joint(side=side, name=name, parent=ctl)
    return ctl


def createFKChain(jntList, side="C", name="name", segmentList=[], parent=None):
    ''' 
        ParentGRP>
                for each elem in the jntList
                    OFS>JNT>CTL_SHAPE
    '''
   

    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)

    jntChainList=[]
    root=grp
    # Creating JNT
    for i, jnt in enumerate(jntList):
        if (len(segmentList)==len(jntList)):
            ofs = mmod.transform(side=side, name=name+"_"+segmentList[i], type="OFS", parent=root)
            # Matching orientation GUIDE > OFS
            fn.align(jnt, ofs)
           
            newJnt = mmod.joint(side=side, name=name+"_"+segmentList[i], parent=ofs)
            jntChainList.append(newJnt)
            # Creating Circle
            if (i==len(jntList)-1):
                break
            circle = mmod.circle( side=side, name=name+"_"+segmentList[i], parent=None)
            # Scaling Ctrl
            fn.scaleShapePoints(circle.name, mc.getAttr(jnt+".radius")/2)
            # fn.rotateShapePoints(circle.name, rotationVector=[90, 0, 0], pivot=mc.xform(jnt, q=True, ws=True, t=True))
            fn.rotateShapePoints(circle.name, rotationVector=[0, 90, 0], pivot=mc.xform(jnt, q=True, ws=True, t=True))

            circleShape=mc.listRelatives(circle.name, c=True)
            mc.parent (circleShape, newJnt.name, r=True, s=True)
            mc.delete(circle.name)
            root = newJnt
        else:
            ofs = mmod.transform(side=side, name=name, type="OFS", parent=root)
            # Matching orientation GUIDE > OFS
            fn.align(jnt, ofs)
            newJnt = mmod.joint(side=side, name=name, parent=ofs)
            jntChainList.append(newJnt)
            if (i==len(jntList)-1):
                break
           
            circle = mmod.circle( side=side, name=name, parent=None)
            # Scaling Ctrl
            fn.scaleShapePoints(circle.name, mc.getAttr(jnt+".radius")/2)
            # fn.rotateShapePoints(circle.name, rotationVector=[90, 0, 0], pivot=mc.xform(jnt, q=True, ws=True, t=True))
            fn.rotateShapePoints(circle.name, rotationVector=mc.xform(jnt, q=True, ws=True, ro=True), pivot=mc.xform(jnt, q=True, ws=True, t=True))

            circleShape=mc.listRelatives(circle.name, c=True)
            mc.parent (circleShape, newJnt.name, r=True, s=True)
            mc.delete(circle.name)
            root = newJnt
    return jntChainList


def createIKHandle(jnt, endEffector, side="C", name="name", parent=None):
    ''' Creating and remaming the IK Handle elements'''
   

    ik = mc.ikHandle(jnt, ee=endEffector, n=side+"_"+name+"00_IKH")
    mc.rename(ik[1], side+"_"+name+"Effector00_IKE")
    if parent!=None:
        mc.parent(ik[0], parent)
        # Clear mmod.transformations
        mc.setAttr(ik[0]+".translateX",0)
        mc.setAttr(ik[0]+".translateY",0)
        mc.setAttr(ik[0]+".translateZ",0)

    return ik[0]


######### Script for creating even jnts #########
def getSideFromParent(obj):

    # getting side
    if ("L_" in obj):
        side = "L"
    elif("R_" in obj):
        side = "R"
    else:
        side="C"

    
    return side, name, type
def insetJnt(startJnt=None, endJnt=None, numbJnt=1):
    # get length
    len = mc.getAttr(endJnt+".translateX")
    individualLen = len/numbJnt
    prevJnt = startJnt
    for i in range (numbJnt):
        jnt = mmod.joint(side="C", name="name", parent= prevJnt)
        mc.xform(jnt, t=[individualLen, 0, 0])
        prevJnt = jnt



# insetJnt(startJnt="C_tail01_JNT", endJnt="C_tail029_JNT", numbJnt=)

