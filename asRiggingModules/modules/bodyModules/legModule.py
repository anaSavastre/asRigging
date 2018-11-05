''' 
            Leg module
                        Ana Maria Savastre
                        Bournemouth University 

Module that creates the leg

GUIDE REQUIREMENTS

IMPLEMENTATION:
    1. Limited foot (foot doesn't go bewond the max distance of the jnt chain)

'''
import maya.cmds as mc
import mayaModule as mmod
import functions as fn
# import loadFn as loadFn
# TEMPORARY

componetFile = "D:/Bournemouth University/asRigging/projects/masterClass/rigging/Spinosaurus/wip/components/SpinosaurusComponents.0001.ma"
referenceFile = "D:/Bournemouth University/asRigging/projects/masterClass/models/Spinosaurus/Spinosaurus.ma"

# NEW SCENE
mc.file(new = True, f=True)

# IMPORT MODEL
mc.file(componetFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)
# ReferenceModel
mc.file(referenceFile, r=True, type="mayaAscii", namespace = "Spinosaurus")


# TEMP FUNCTIONS
def getParent(grp):
    '''
    Returns parent of given transform node in the outliner 
    '''
    return mc.listRelatives(grp, p=True)

def resetJNTCount():
    mmod.joint.elemIndex = 0

def resetTRNCount():
    mmod.transform.elemIndex = 0

def createIKHandle(jnt, endEffector, side="C", name="name", parent=None):
    ik = mc.ikHandle(jnt, ee=endEffector, n=side+"_"+name+"00_IKH")
    mc.rename(ik[1], side+"_"+name+"Effector00_IKE")
    mc.parent(ik[0], parent)
    print ik


def constructCTL(guideJNT, side="C", name="name", parent=None):
    '''
    Function that creates the following hierarchy 
    transformNode_GRP
        transformNode_OFS : aligned with guideJNT
            circle_CTL
                JNT_obj 
    '''
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(guideJNT, ofs)

    # Creating CTL
    ctl = mmod.circle(side=side, name=name, parent=ofs)
    # Creating JNT
    jnt = mmod.joint(side=side, name=name, parent=ctl)

    return ctl


def createJntChain(jntList, side="C", name="name", segmentList=[], parent=None):
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(jntList[0], ofs)

    jntChainList=[]
    # Creating JNT
    for i, jnt in enumerate(jntList):
        if (len(segmentList)==len(jntList)):
            newJnt = mmod.joint(side=side, name=name+segmentList[i], parent=ofs if i==0 else newJnt)
            fn.align(jnt, newJnt)
            mc.makeIdentity(newJnt, r=True, apply=True)
            jntChainList.append(newJnt)
        else:
            newJnt = mmod.joint(side=side, name=name, parent=ofs if i==0 else newJnt)
            fn.align(jnt, newJnt)
            mc.makeIdentity(newJnt, r=True, apply=True)
            jntChainList.append(newJnt)
    return jntChainList


def constructJNT(guideJNT, side="C", name="name", parent=None):
    '''
    Function that creates the following hierarchy 
    transformNode_GRP
        transformNode_OFS : aligned with guideJNT
            JNT_obj 
    '''
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(guideJNT, ofs)

    # Creating JNT
    jnt = mmod.joint(side=side, name=name, parent=ofs)

    return jnt


def descendentsList(root=None):
    descendentsList = mc.listRelatives(root, ad=True)
    descendentsList.append(root)
    descendentsList.reverse()
    return descendentsList


class leg(object):
    def __init__(self, side="C", legName="leg", legJnt=None, footJnt=None, ankleGuide=None, parent=None):
        '''
        NAMES
        legSegments ={hip, knee, ankle}


        1. HIERARCHY STRUCTURE
            legName_GRP
                > Settings_GRP: addAttr(length01, length12...)
                > legJoints_GRP    
                        hip_GRP>OFS>JNT
                            knee_GRP>OFS>CTL>JNT
                                ankle_GRP>OFS>CTL>JNT
                > ankleCtrl_GRP>OFS>CTL
                > limitedAnkle_GRP
                        cube (temp for testing)
                        footJointsGRP>>>>
                        IKHandle

        2. SET UP
            Creating joints form guides
            Creating IK Handle
            Limited ankle set-up
                            
        '''

        # GLOBALS
        resetJNTCount()
        resetTRNCount()

        legSegments = ["Hip", "Knee", "Ankle"]
        legJNTList = descendentsList(root=legJnt)
       

        # 1.CREATING HIERARCHY
        legGRP = mmod.transform(side=side, name=legName, type="GRP", parent=parent)
        legJntGRP = mmod.transform(side=side, name=legName+"Joints", type="GRP", parent=legGRP)
        limitedAnkleGRP = mmod.transform(side=side, name=legName+"LimitedAnkle", type="GRP", parent=legGRP)
        ankleCtrl = constructCTL(ankleGuide, side=side, name="Ankle", parent=legGRP)
        settingsGRP = mmod.transform(side=side, name=legName+"Settings", type="GRP", parent=legGRP)

        # Leg jnt chain
        jntChain = createJntChain(legJNTList, side=side, name=legName, segmentList=legSegments, parent=legJntGRP)
        
        # IK Handle
        ikHandle = createIKHandle(jntChain[0], jntChain[len(jntChain)-1], side=side, name=legName+"IKHandle", parent=limitedAnkleGRP)

        # 


        # TEMP: FOR VISUALIZATION
        cube = mc.polyCube(n="limitedAnkle", w=10, h=10, d=10)[0]
        mc.parent (cube, limitedAnkleGRP)
        mc.setAttr(cube+".translateX", 0)
        mc.setAttr(cube+".translateY", 0)
        mc.setAttr(cube+".translateZ", 0)
         
        
        
        # DELETING GUIDES
        # mc.delete(legJnt)
        mc.hide(legJnt, ankleGuide)
        ############################################################### TO DELETE ###############################################################
        # # Leg jnt chain
        # for i, jnt in enumerate(legJNTList):
        #     newJoint = constructJNT(jnt, side=side, name=legName+legSegments[i], parent=legJntGRP if i==0 else newJoint)
        #     # Setting raius of joint
        #     # newJoint.radius = 10
        ############################################################### TO DELETE ###############################################################



L_leg = leg(legJnt="L_legHip00_JNT", legName="leg", ankleGuide="L_legAnkleGuid00_LOC", side="L")
