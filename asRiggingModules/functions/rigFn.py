import maya.cmds as mc
import functions as fn
import mayaModule as mmod



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

def constructCTL(guideJNT, side="C", name="name", parent=None, ctrlScale=1):
    '''
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
    ctl = mmod.circle(side=side, name=name, parent=ofs)
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
            fn.scaleShapePoints(circle.name, mc.getAttr(jnt+".radius"))
            # fn.rotateShapePoints(circle.name, rotationVector=[90, 0, 0], pivot=mc.xform(jnt, q=True, ws=True, t=True))
            fn.rotateShapePoints(circle.name, rotationVector=mc.xform(jnt, q=True, ws=True, ro=True), pivot=mc.xform(jnt, q=True, ws=True, t=True))

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
            fn.scaleShapePoints(circle.name, mc.getAttr(jnt+".radius"))
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
