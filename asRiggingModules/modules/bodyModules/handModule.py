import maya.cmds as mc

import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import mayaNode as node
import asNodes as asNode


# TEMPORARY

# componetFile = "D:/Bournemouth University/asRigging/tmp/masterClass/prePrp_hand_TEST/fingerComponent03.ma"

# # NEW SCENE
# mc.file(new = True, f=True)

# # IMPORT MODEL
# mc.file(componetFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)



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
    globalCtrl=None
    def __init__(self, jntHierarchy, fingerName="finger", side="C", parent=None, hook=None, worldUpVector=""):
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
        self.side = side
        self.parent = parent
        self.hook = hook
        self.worldUpVector = worldUpVector
        mmod.resetCount()

        metacarpalName = fingerName+"Metacarpal"
        phalangeName = [fingerName+"ProximalPhalange", fingerName+"MiddlePhalange", fingerName+"DistalPhalange"] 
        guidJntList = mc.listRelatives(jntHierarchy, ad=True); guidJntList.reverse()
        fingerBaseJnt=[]

        aimVector = [1, 0, 0]
        upVector = [0, 1, 0]
                

        # CREATING HIERARCHY
        self.fingerGRP = mmod.transform(side=side, name=fingerName, type="GRP", parent=parent)
        # worldUpVector
        
        # GLOBAL CTRL
        if (fingerName=="pinky"):
            finger.globalCtrl = rigFn.constructCTL(jntHierarchy, side=side, name=metacarpalName, parent=self.fingerGRP)
            #metaJntA = fn.getChildren(self.globalCtrl.name)[1]
            #fingerBaseJnt.append(metaJntA)

        metaJntA = rigFn.constructJNT(jntHierarchy, side=side, name=metacarpalName, parent=self.fingerGRP)
        fingerBaseJnt.append(metaJntA.name)

        # METACARPAL JNT        
        metaJntB = mmod.joint(side=side, name=metacarpalName, parent=metaJntA)
        metaJntB.translateX=mc.xform(guidJntList[0], q=True, r=True, t=True)[0]
        metaGrp = mmod.transform(side=side, name=metacarpalName, parent=fn.getParent(metaJntA), type="GRP")
        mc.parent(metaJntA, metaGrp)
        
        # PHALANGES JNT
        for i, jnt in enumerate(guidJntList[:-1]):
            phalangeCTL = rigFn.constructCTL(jnt, side=side, name=phalangeName[i], parent=fn.getParent(metaJntA) if i==0 else phalangeCTL)
            fingerBaseJnt.append(mc.listRelatives(phalangeCTL, c=True, typ="joint")[0])
            jntB = mmod.joint(side=side, name=phalangeName[i], parent=fingerBaseJnt[i+1])

            # AIM CONSTRAINTS
            # Creating WorldUpObject
            worldUpObj = mmod.transform(side=self.side, name=fingerName+str(i)+"WorldUpObject", parent=fn.getParent(fingerBaseJnt[i]))
            fn.snapTool(fingerBaseJnt[i], worldUpObj)
            mc.aimConstraint(fingerBaseJnt[i+1], fingerBaseJnt[i], aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=worldUpObj)

            
            # JOINT STRETCHING
            distanceBetweenNode = mc.createNode("distanceBetween", name=side+"_distance"+fingerName+str(i)+"_DST")
            #print fingerBaseJnt[i], "jnt"
            mc.connectAttr(fingerBaseJnt[i]+".worldMatrix", distanceBetweenNode+".inMatrix1")
            mc.connectAttr(fingerBaseJnt[i+1]+".worldMatrix", distanceBetweenNode+".inMatrix2")

            # Minus operation
            minusNode = mc.createNode("plusMinusAverage", name=side+"_subtract"+fingerName+str(i)+"_PMA")
            mc.setAttr(minusNode+".operation", 2)
            mc.connectAttr(distanceBetweenNode+".distance", minusNode+".input1D[0]")
            mc.connectAttr(fingerBaseJnt[i+1]+".radius", minusNode+".input1D[1]")
            # Scalingby global scale
            divide = mNode.multiplyDivide(side=self.side, name=fingerName+str(i)+"GlobalScale")
            worldTransformation = mNode.decomposeMatrix(side=self.side, name = "rootGlobalTransformation")
            mmod.connectAttr(self.hook.name+".worldMatrix", worldTransformation.getInputMatrix())
            mmod.connectAttr(minusNode+".output1D", divide.name+".input1X")
            divide.operation = 2
            mmod.connectAttr(worldTransformation.getOutputScale(), divide.getInput2())
            mc.connectAttr(divide.name+".outputX", fn.getChildren(fingerBaseJnt[i])[0]+".translateX")

            # POSITIONING END JNT
            if (jnt==guidJntList[-2]):
                translateX = mc.getAttr(guidJntList[-1]+".translateX")
                mc.setAttr(fn.getChildren(fingerBaseJnt[-1])[0]+".translateX", translateX)


        self.fingerJntChain = fingerBaseJnt

        # DELETING GUIDES
        mc.delete(jntHierarchy)

class hand():

    def __init__(self, handJnt=None, side="C", name="hand", parent=None, root=None, hook=None):
        '''
        Hand Module
        parent = object to parent too
        root = arm 
        hook = rootJnt for global scale

        Creating a finger obj for each of the jnt Chain in the hierarchy 
        '''
        # SELF
        self.side = side
        self.name = name
        self.handJnt = hand
        self.parent = parent
        self.root = root
        self.hook = hook

        # GLOBALS
        mmod.resetCount()


        # CREATING HIERARCHY
        handGrp = mmod.transform(side=self.side, name="hand", type="GRP", parent=self.parent)
        self.handGrp = handGrp

        # CONNECTING HAND GROUP TO WRIST MOVEMENT
        self.connectToWristMovement()

        # CREATING FINGERS
        fingerJntList = fn.getChildren(handJnt)
        fingers=[]
        for jnt in fingerJntList:
            name = fn.concat_str(jnt, s1_begin = 2, s1_end=6)
            fingerObj = finger(jnt, fingerName=name, side=self.side, parent=handGrp, hook=self.hook)
            fingers.append(fingerObj)

        # CREATE GLOBAL ROTATE
        for i, f in enumerate(fingers):
            '''if (i==0):
                mmod.connectAttr(finger.globalCtrl.name+'.rotateZ', fn.getParent(f.fingerJntChain[0])+'.rotateZ')
            else:'''
        
            # CREATING SCALING FACTOR
            multNode = mNode.multDoubleLinear(side=self.side, name="globalRotateScalingFactor")
            mmod.connectAttr(finger.globalCtrl.name+'.rotateZ', multNode.getInput1())
            mc.setAttr(multNode.getInput2(), (i*20)/100.0+0.05)
            mmod.connectAttr(multNode.getOutput(), fn.getParent(f.fingerJntChain[0])+'.rotateZ')
        # DELETING GUIDES
        mc.delete(handJnt)
    def connectToWristMovement(self):
        # CONNECTING TRANSLATION
        # Getting Local Space
        matrixMult = mNode.multMatrix(side=self.side, name=self.name+"LocalSpace")
        decopMatrix = mNode.decomposeMatrix(side=self.side, name=self.name+"LocalSpace")
        mmod.connectAttr(self.root.bindJntChain[-1].name+".worldMatrix", matrixMult.name+".matrixIn[0]")
        mmod.connectAttr(self.parent+".worldInverseMatrix", matrixMult.name+".matrixIn[1]")
        mmod.connectPlugs(matrixMult.matrixSum, decopMatrix.inputMatrix)
        mmod.connectPlugs(decopMatrix.outputTranslate, self.handGrp.translate)
        # CONNECTING ROTATION
        additive = mNode.animBlendNodeAdditiveDA(side=self.side, name=self.name+"ReverseRotationX")
        mmod.connectAttr(self.root.effectorCtrl.name+".rotateX", additive.getInputA())
        additive.weightA = -1
        mmod.connectAttr(additive.getOutput(), self.handGrp.name+".rotateZ")
        mmod.connectAttr(self.root.effectorCtrl.name+".rotateY", self.handGrp.name+".rotateY")
        mmod.connectAttr(self.root.effectorCtrl.name+".rotateZ", self.handGrp.name+".rotateX")
