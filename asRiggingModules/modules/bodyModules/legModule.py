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
import functions as fn
import mayaModule as mmod


# TEMPORARY

componetFile = "D:/Bournemouth University/asRigging/projects/masterClass/rigging/Spinosaurus/wip/components/SpinosaurusComponents.0002.ma"
referenceFile = "D:/Bournemouth University/asRigging/projects/masterClass/models/Spinosaurus/Spinosaurus.ma"

# NEW SCENE
mc.file(new = True, f=True)

# IMPORT MODEL
mc.file(componetFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)
# ReferenceModel
mc.file(referenceFile, r=True, type="mayaAscii", namespace = "Spinosaurus")


# TEMP FUNCTIONS
def rotateShapePoints(shape, rotationVector=[0, 0, 0], pivot=[0, 0, 0]):
    print "rotation", rotationVector
    print pivot    
    mc.xform(shape+".cv[0:*]", ro=rotationVector, rp = pivot, os=True)


def resetJNTCount():
    mmod.joint.elemIndex = 0

def resetTRNCount():
    mmod.transform.elemIndex = 0

def createIKHandle(jnt, endEffector, side="C", name="name", parent=None):
    ik = mc.ikHandle(jnt, ee=endEffector, n=side+"_"+name+"00_IKH")
    mc.rename(ik[1], side+"_"+name+"Effector00_IKE")
    if parent!=None:
        mc.parent(ik[0], parent)
        # Clear mmod.transformations
        mc.setAttr(ik[0]+".translateX",0)
        mc.setAttr(ik[0]+".translateY",0)
        mc.setAttr(ik[0]+".translateZ",0)

    return ik[0]


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
            2.1. Creating joints form guides
            2.2. Creating IK Handle
            2.3. Limited ankle set-up
                            
        '''

        # GLOBALS
        resetJNTCount()
        resetTRNCount()
        legSegments = ["Hip", "Knee", "Ankle"]
        legJNTList = descendentsList(root=legJnt)
       

        # 1. CREATING HIERARCHY
        legGRP = mmod.transform(side=side, name=legName, type="GRP", parent=parent)
        legJntGRP = mmod.transform(side=side, name=legName+"Joints", type="GRP", parent=legGRP)
        limitedAnkleGRP = mmod.transform(side=side, name=legName+"LimitedAnkle", type="GRP", parent=legGRP)
        ankleCtrl = constructCTL(ankleGuide, side=side, name=legName+"Ankle", parent=legGRP, ctrlScale=mc.getAttr(legJNTList[2]+".radius"))
        ankleJNT = mc.listRelatives(ankleCtrl)[0]
        settingsGRP = mmod.transform(side=side, name=legName+"Settings", type="GRP", parent=legGRP)

        # Position Ctrl
        rotateShapePoints(ankleCtrl.name, rotationVector=[90, 0, 0], pivot=mc.xform(legJNTList[2], q=True, t=True, ws=True))

        # 2. SET UP
        # 2.1. LEG JNT CHAIN
        jntChain = createJntChain(legJNTList, side=side, name=legName, segmentList=legSegments, parent=legJntGRP)
        
        # 2.2. IK Handle
        ikHandle = createIKHandle(jntChain[0], jntChain[len(jntChain)-1], side=side, name=legName+"IKHandle", parent=limitedAnkleGRP)
        
        # ikHandle = createIKHandle(jntChain[0], jntChain[len(jntChain)-1], side=side, name=legName+"IKHandle")
        
        # 2.3. Limited IK
        # Settings GRP
        # Get bone length
        femurLength = jntChain[1].getTranslateX()
        tibiaLength = jntChain[2].getTranslateX()
        # String to worldMatrix Attr
        hipWorldMatrixAttr = jntChain[0].getWorldMatrix()
        # hipWorldMatrixValue = mc.getAttr(hipWorldMatrixAttr)
        # print "matrixValue", hipWorldMatrixValue
        # Add attr
        femurLengthAttr     = settingsGRP.addAttr( longName="femurLength", softMinValue=0, defaultValue=femurLength, softMaxValue=2*femurLength, attrType="double", keyable=True)
        tibiaLengthAttr     = settingsGRP.addAttr( longName="tibiaLength", softMinValue=0, defaultValue=tibiaLength, softMaxValue=2*tibiaLength, attrType="double", keyable=True)
        hipStartMatrixAttr  = settingsGRP.addAttr(longName="hipStartMatrix", attrType="matrix")
        mmod.connectAttr(hipWorldMatrixAttr, settingsGRP.name+".hipStartMatrix")
        mc.disconnectAttr(hipWorldMatrixAttr, settingsGRP.name+".hipStartMatrix")
        # mc.setAttr(hipWorldMatrixAttr, hipWorldMatrixValue, type="matrix")
        
        # Connect attr
        mmod.connectPlugs(femurLengthAttr, jntChain[1].translateX)
        mmod.connectPlugs(tibiaLengthAttr, jntChain[2].translateX)
        
        # AddDoubleLiniar: femour.len+tibia.len
        maxLength = mmod.addDoubleLinear(side=side, name="legMaxLength")
        mmod.connectAttr(settingsGRP.name+".femurLength", maxLength.getInput1())
        mmod.connectAttr(settingsGRP.name+".tibiaLength", maxLength.getInput2())
        
        # DecompMatrix: anlkeJNT.worldMatrix
        ankleWorldDecompose = mmod.decomposeMatrix(side=side, name="ankleWorldMatrix") 
        mmod.connectAttr(ankleJNT+".worldMatrix", ankleWorldDecompose.getInputMatrix())

        # DecompMatrix: hipStartMatrixAttr
        hipWorldMatrixDecompose = mmod.decomposeMatrix(side=side, name="hipWorldMatrix")
        mmod.connectPlugs(hipStartMatrixAttr, hipWorldMatrixDecompose.inputMatrix)

        # PlusMinusAverage: get the vector between the hip and the ankle
        ankleHipVecDir = mmod.plusMinusAverage(side=side, name="hipAngleVecDir")
        # Subtraction Operation
        ankleHipVecDir.operation = 2 
        mmod.connectAttr(ankleWorldDecompose.getOutputTranslate, ankleHipVecDir.name+".input3D[0]")
        mmod.connectAttr(hipWorldMatrixDecompose.getOutputTranslate, ankleHipVecDir.name+".input3D[1]")

        # VectorProduct: normalize hip ankle vector
        vectorNormalize = mmod.vectorProduct(side=side, name="hipAnkleVectorNormalize")
        vectorNormalize.operation = 0
        vectorNormalize.normalizeOutput = 1
        mmod.connectPlugs(ankleHipVecDir.output3D, vectorNormalize.input1)


        # DistanceBetween: hipStartMatrix and ankle( child of ankle_CTL)
        hipAnkleDist = mmod.distanceBetween(side=side, name="hipAnkle")
        mmod.connectPlugs(hipStartMatrixAttr, hipAnkleDist.inMatrix1)
        mmod.connectAttr(ankleJNT+".worldMatrix", hipAnkleDist.getInMatrix2())

        # Clamp: distance to max = length(femour.len+tibia.len)
        distancedClamp = mmod.clamp(side=side, name="hipAnkleDist")
        mmod.connectPlugs(hipAnkleDist.distance, distancedClamp.inputR)
        mmod.connectPlugs(maxLength.output, distancedClamp.maxR)

        # MultiplyDivide: ankleHipVecDir*ankleHipMaxLength  
        multiplyDivideNode = mmod.multiplyDivide(side=side, name="hipAnkleVector")
        mmod.connectAttr(vectorNormalize.getOutput(), multiplyDivideNode.getInput1())
        mmod.connectAttr(distancedClamp.getoutputR(), multiplyDivideNode.getInput2()+".input2X")
        mmod.connectAttr(distancedClamp.getoutputR(), multiplyDivideNode.getInput2()+".input2Y")
        mmod.connectAttr(distancedClamp.getoutputR(), multiplyDivideNode.getInput2()+".input2Z")

        # PlusMinusAverage: ankleHipVec in local space of hip
        plusNode = mmod.plusMinusAverage(side=side, name="localizeHipAnkleVector")
        mmod.connectAttr(multiplyDivideNode.getOutput(), plusNode.name+".input3D[0]")
        mmod.connectAttr(hipWorldMatrixDecompose.getOutputTranslate, plusNode.name+".input3D[1]")
        mmod.connectAttr(plusNode.name+".output3D", limitedAnkleGRP.name+".translate")


        # # TEMP: FOR VISUALIZATION
        # cube = mc.polyCube(n="limitedAnkle", w=10, h=10, d=10)[0]
        # mc.parent (cube, limitedAnkleGRP)
        # mc.setAttr(cube+".translateX", 0)
        # mc.setAttr(cube+".translateY", 0)
        # mc.setAttr(cube+".translateZ", 0)
         
        
        
        # DELETING GUIDES
        mc.delete(legJnt, ankleGuide)
   

L_leg = leg(legJnt="L_legHip00_JNT", legName="leg", ankleGuide="L_legAnkleGuid00_LOC", side="L")
