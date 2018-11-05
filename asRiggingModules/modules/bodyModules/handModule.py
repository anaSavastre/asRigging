import maya.cmds as mc

import mayaModule as mmod
import functions as fn


# TEMPORARY

componetFile = "D:/Bournemouth University/asRigging/tmp/masterClass/prePrp_hand_TEST/fingerComponent03.ma"

# NEW SCENE
mc.file(new = True, f=True)

# IMPORT MODEL
mc.file(componetFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)



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



def createJointHY(side="C", name="name", parent=None):
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)
    # loading ctrl
    objInScene = mc.ls("*_CTL")
    mc.file(controlShapesPath+"/"+name+"Control.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)
    newObjInScene = mc.ls("*_CTL")
    if (len(newObjInScene)-len(objInScene)==1):
        ctrl= [obj for obj in newObjInScene if obj not in objInScene]
    mc.parent(ctrl, ofs)
    return ctrl


def constructCTL(guideJNT, side="C", name="name", parent=None):
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(guideJNT, ofs)

    # Creating CTL
    ctl = mmod.circle(side=side, name=name, parent=ofs)
    # Creating JNT
    jnt = mmod.joint(side=side, name=name, parent=ctl)

    return ctl




def constructJNT(guideJNT, side="C", name="name", parent=None):
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)

    # Matching orientation GUIDE > OFS
    fn.align(guideJNT, ofs)

    # Creating JNT
    jnt = mmod.joint(side=side, name=name, parent=ofs)

    return jnt




class finger(object):
    def __init__(self, jntHierarchy, fingerName="finger", side="C", parent=None, worldUpVector=""):
        '''
        NAMES
        fingerName ={thumb, index, middle, ring, pinky}


        1. HIERARCHY STRUCTURE
            fingerName_GRP
                metacarpal_GRP>OFS>JNT
                    phalangeA00_GRP>OFS>CTL>JNT
                        phalangeB00_GRP>OFS>CTL>JNT
                            phalangeC00_GRP>OFS>CTL>JNT
                         
        '''

        # GLOBALS
        resetJNTCount()
        resetTRNCount()

        metacarpalName = fingerName+"_metacarpal"
        phalangeName = [fingerName+"_proximalPhalange", fingerName+"_middlePhalange", fingerName+"_distalPhalange"] 
        guidJntList = mc.listRelatives(jntHierarchy, ad=True); guidJntList.reverse()
        fingerBaseJnt=[]

        aimVector = [1, 0, 0]
        upVector = [0, 1, 0]
                


        # # CONSTRUCTOR
        # self.jnt

        # CREATING HIERARCHY
        fingerGRP = mmod.transform(side=side, name=fingerName, type="GRP", parent=parent)
        # worldUpVector

        # METACARPAL JNT
        
        metaJntA = constructJNT(jntHierarchy, side=side, name=metacarpalName, parent=fingerGRP)
        metaJntB = mmod.joint(side=side, name=metacarpalName, parent=metaJntA)
        metaJntB.translateX=mc.xform(guidJntList[0], q=True, r=True, t=True)[0]
        fingerBaseJnt.append(metaJntA.name)

        # PHALANGES JNT
        for i, jnt in enumerate(guidJntList[:-1]):
            phalangeCTL = constructCTL(jnt, side=side, name=phalangeName[i], parent=getParent(metaJntA) if i==0 else phalangeCTL)
            fingerBaseJnt.append(mc.listRelatives(phalangeCTL, c=True, typ="joint")[0])
            jntB = mmod.joint(side=side, name=phalangeName[i], parent=fingerBaseJnt[i+1])

            # AIM CONSTRAINTS
            print "aim", fingerBaseJnt[i], fingerBaseJnt[i+1]
            mc.aimConstraint(fingerBaseJnt[i+1], fingerBaseJnt[i], aim=[1, 0, 0], u=[0, 1, 0])

            
            # JOINT STRETCHING
            distanceBetweenNode = mc.createNode("distanceBetween", name=side+"_distance"+fingerName+str(i)+"_DST")
            mc.connectAttr(fingerBaseJnt[i]+".worldMatrix", distanceBetweenNode+".inMatrix1")
            mc.connectAttr(fingerBaseJnt[i+1]+".worldMatrix", distanceBetweenNode+".inMatrix2")

            # Minus operation
            minusNode = mc.createNode("plusMinusAverage", name=side+"_subtract"+fingerName+str(i)+"_PMA")
            mc.setAttr(minusNode+".operation", 2)
            mc.connectAttr(distanceBetweenNode+".distance", minusNode+".input1D[0]")
            mc.connectAttr(fingerBaseJnt[i+1]+".radius", minusNode+".input1D[1]")
            mc.connectAttr(minusNode+".output1D", fn.getChildren(fingerBaseJnt[i])[0]+".translateX")


        

        # DELETING GUIDES
        mc.delete(jntHierarchy)
        # mc.hide(jntHierarchy)




class hand():

    def __init__(self, jntHierarchy, side):
        pass

        # CREATING HIERARCHY


L_finger1 = finger("L_metacarpal00_JNT", fingerName="index", side="L")

R_finger1 = finger("R_metacarpal00_JNT", fingerName="index", side="R")