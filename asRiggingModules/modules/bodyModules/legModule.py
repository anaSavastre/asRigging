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
import rigFn as rigFn


# TEMPORARY

componetFile = "D:/Bournemouth University/asRigging/projects/masterClass/rigging/Spinosaurus/wip/components/SpinosaurusComponents.0005.ma"
referenceFile = "D:/Bournemouth University/asRigging/projects/masterClass/models/Spinosaurus/Spinosaurus.ma"

# NEW SCENE
mc.file(new = True, f=True)

# IMPORT MODEL
mc.file(componetFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)
# ReferenceModel
# mc.file(referenceFile, r=True, type="mayaAscii", namespace = "Spinosaurus")


# TEMP FUNCTIONS

class multDoubleLinear(mmod.utilityNode):
    elemIndex = 0
    nodeType = "multDoubleLinear"
    def __init__(self, side="C", name="multDoubleLinear", type ="MTL"):
        super(multDoubleLinear, self).__init__(self.nodeType, side, name, type)
        multDoubleLinear.elemIndex+=1

    # INPUT ATTRIBUTES
    def getInput1(self):
            return self.name+".input1"
    @property
    def input1(self):
        ''' returns node's plug '''
        return self.getPlug("input1")
    @input1.setter
    def input1(self, value):
        mc.setAttr(self.name+".input1", value)

    def getInput2(self):
        return self.name+".input2"
    @property
    def input2(self):
        ''' returns node's plug '''
        return self.getPlug("input2")
    @input1.setter
    def input2(self, value):
        mc.setAttr(self.name+".input2", value)
    
    # OUTPUT ATTRIBUTES
    def getOutput(self):
        return self.name+".output"
    @property
    def output(self):
        ''' returns node's plug '''
        return self.getPlug("output")
    @output.setter
    def output(self, value):
        mc.setAttr(self.name+".output", value)

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
def resetJNTCount():
    mmod.joint.elemIndex = 0

def resetTRNCount():
    mmod.transform.elemIndex = 0

def planeEquation(p1, p2, p3):
    ''' 
    ax + by + cz + d = 0

    a = (y2z3 - y3z2) + (y3z1 - y1z3) + (y1z2 - y2z1)
    b = (z2x3 - z3x2) + (z3x1 - z1x3) + ()
    
    '''

    a = (p2[1]*p3[2] - p3[1]*p2[2]) + (p3[1]*p1[2] - p1[1]*p3[2]) + (p1[1]*p2[2] - p2[1]*p1[2])
    b = (p2[2]*p3[0] - p3[2]*p2[0]) + (p3[2]*p1[0] - p1[2]*p3[0]) + (p1[2]*p2[0] - p2[2]*p1[0])
    c = (p2[2]*p3[1] - p3[0]*p2[1]) + (p3[0]*p1[1] - p1[0]*p3[1]) + (p1[0]*p2[1] - p2[0]*p1[1])
    d = -a*p1[0] - b*p1[1] - c*p1[2]
    return [a, b, c, d]

class foot(object):
    def __init__(self, side="C", footJnt=None, ankleCTL=None, parent=None, hook=None):
        # self
        self.side = side
        self.footJnt = footJnt
        self.ankleCTL = ankleCTL
        self.parent = parent
        self.footSegments = ["Ankle", "Toes", "ToesEnd"]
        self.footName="foot"
        
        if (footJnt):
            # FK Foot            
            footJNTList = fn.descendentsList(root=footJnt)
            self.FKfoot_setUp(footJNTList=footJNTList, parent=parent)
            # FOOT ROLL
            self.footRoll_setUp(footJNTList=footJNTList)


            # DELETING GUIDES
            # mc.hide(footJnt)


    def footRoll_setUp(self, footJNTList=[], parent=None):
        ''' 
            0. Creating heel jnt from the guides
                Create jnt on the plane defined by the three guides
                HeelJnt : y of toe end, z of ankle, 
                => x=?

            1. CREATING THE HIERARCHY
                footRollGRP
                    >control
                        >animParameters (footRoll, tarsalLock, strainghten)
                        >configParameters (toeRest, tarsalRest, heelLength, toeLength, tarsalLength)
                    >joints

            2. SETTING UP FOOT ROLL
                2.0. Creating Jnts
                2.1. Creating control attr
                2.2. Linking control Attr

            3. FOOT ROLL NETWORK

            4. CONNECT FOOTROLL TO LEG
        '''
        # GLOBALS
        resetJNTCount()
        resetTRNCount()
        # CREATING HEEL JNT
        # Getting the plane defined by the guides
        # Getting the 3 points
        p1 = mc.xform(footJNTList[0], ws=True, q=True, t=True)
        p2 = mc.xform(footJNTList[1], ws=True, q=True, t=True)
        p3 = mc.xform(footJNTList[2], ws=True, q=True, t=True)
        plane = planeEquation(p1, p2, p3)
        # Finding x of heel jnt
        y = p3[1]; z = p1[2]
        x = -(plane[3] + plane[2]*z + plane[1]*y)/plane[0]
        heelJnt = mmod.joint(side=self.side, name=self.footName+"Heel", parent=None)
        mc.xform(heelJnt.name, ws=True, t=[x, y, z])
        # Aiming heel to toeEnd
        mc.delete(mc.aimConstraint(footJNTList[2], heelJnt, aim=[-1, 0, 0], u=[0, 1, 0], worldUpType="scene"))

        # 1. CREATING HIERARCHY
        globalFootRoll = mmod.transform(side=self.side, name=self.footName+"Roll", type="GRP", parent=parent)
        controlGrp = mmod.transform(side=self.side, name=self.footName+"Roll_controls", type="GRP", parent=globalFootRoll)
        jointsGrp =  mmod.transform(side=self.side, name=self.footName+"Roll_joints", type="GRP", parent=globalFootRoll)
        animParameters = mmod.transform(side=self.side, name=self.footName+"Roll_animParameters", type="GRP", parent=controlGrp)
        configParameters = mmod.transform(side=self.side, name=self.footName+"Roll_configParameters", type="GRP", parent=controlGrp)

        # 2.0. Creating Joints
        footJNTList.append(heelJnt)
        footJNTList.reverse()
        segments = self.footSegments
        segments.append("Heel")
        segments.reverse()
        newGuides = jntHierarchy(footJNTList)
        footRolljnt = rigFn.createJntChain(newGuides, side=self.side, name=self.footName, segmentList = segments, parent=jointsGrp)
        mc.delete(newGuides)
        # 2.1. Creating control attr
        footRoll = animParameters.addAttr(longName="footRoll", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        tarsalLock = animParameters.addAttr(longName="tarsalLock", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        straighten = animParameters.addAttr(longName="straighten", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)

        toeRest = configParameters.addAttr( longName="toeRest", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        tarsalRest = configParameters.addAttr( longName="tarsalRest", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)

        mc.setAttr(configParameters.name+".toeRest", mc.getAttr(fn.getParent(footRolljnt[1].name)+".rotateZ"))
        mc.setAttr(configParameters.name+".tarsalRest", mc.getAttr(fn.getParent(footRolljnt[2].name)+".rotateZ"))
        # 2.2. Linking control Attr
        mmod.connectAttr(configParameters.name+".toeRest", fn.getParent(footRolljnt[1].name)+".rotateZ")
        mmod.connectAttr(configParameters.name+".tarsalRest",fn.getParent(footRolljnt[2].name)+".rotateZ")

        # 3. FOOT ROLL NETWORK
        # 3.0. HEEL BACK ROTATION
        clampHeel = mmod.clamp(side=self.side, name="footRollHeel")
        mmod.connectPlugs(footRoll, clampHeel.inputR)
        mc.setAttr(clampHeel.name+".minR", -100)
        inverseMult =multDoubleLinear(side=self.side, name="footRollHeel")
        mmod.connectPlugs(clampHeel.outputR, inverseMult.input1)
        mc.setAttr(inverseMult.name+".input2", -1)
        mmod.connectPlugs(inverseMult.output, footRolljnt[0].rotateZ)
        # 3.1. TARSAL ROTATION
        clampTarsalRot = mmod.clamp(side=self.side, name="footRollTarsalRotation")
        mmod.connectPlugs(footRoll, clampTarsalRot.inputR)
        mmod.connectPlugs(tarsalLock, clampTarsalRot.maxR)
        mmod.connectPlugs(clampTarsalRot.outputR, footRolljnt[2].rotateZ)
        
        # 4. CONNECT FOOTROLL TO LEG


        # DELETING GUIDS
        mc.delete(footJNTList, heelJnt)



        
    def FKfoot_setUp(self, footJNTList=[], parent=None):
        # GLOBALS
        resetJNTCount()
        resetTRNCount()
        # 1. CREATING HIERARCHY
        footFK_GRP = mmod.transform(side=self.side, name=self.footName+"FK", type="GRP", parent=parent)
        footFKJntGRP = mmod.transform(side=self.side, name=self.footName+"FK"+"Joints", type="GRP", parent=footFK_GRP)

        # 2.1. FOOT JNT CHAIN
        jntChain = rigFn.createFKChain(footJNTList, side=self.side, name=self.footName+"FK", segmentList=self.footSegments, parent=footFKJntGRP)
        self.footFKJnt = jntChain

        # 2.2. CONSTRAINING FOOT TO ANKLE
        # mc.parentConstraint(mc.listRelatives(self.ankleCTL, c=True), footFKJntGRP)


class leg(object):
    def __init__(self, side="C", legJnt=None, ankleGuide=None, parent=None, hook=None):
        '''
        NAMES
        legSegments ={hip, knee, ankle}

        1. IK SET-UP

        '''
        # self
        self.side = side
        self.legJnt = legJnt
        self.ankleGuide = ankleGuide
        self.parent = parent
        self.legSegments = ["Hip", "Knee", "AnkleEnd"]
        self.legName="leg"

        # GLOBALS
        resetJNTCount()
        resetTRNCount()
        
        # LEG GRP
        if (legJnt!=None):
            legJNTList = fn.descendentsList(root=legJnt)

            leg_GRP = mmod.transform(side=side, name=self.legName, type="GRP", parent=parent)

            # IK leg
            self.IK_setUp(legJNTList=legJNTList, parent=leg_GRP)

            # FK leg
            self.FK_setUp(legJNTList=legJNTList, parent=leg_GRP)  

            # Bind leg jnt
            self.bindJnt_setUp(legJNTList=legJNTList, parent=hook)
            # FK IK Blend
            # Creating attribute on ctrl
            blendAttr = self.ankleCtrl.addAttr(longName="fkIkBlend", softMinValue=0, defaultValue=1, softMaxValue=1, attrType="double", keyable=True)
            for ikJnt, fkJnt, bindJnt, segment in zip(self.IKjntChain, self.FKjntChain, self.bindJntChain, self.legSegments):
                blendNode = mmod.blendColors(side=self.side, name=segment+"FK_IK", type ="BLD")
                mmod.connectAttr(fkJnt.name+".rotate", blendNode.getColor2())
                mmod.connectAttr(ikJnt.name+".rotate", blendNode.getColor1())
                mmod.connectPlugs(blendAttr, blendNode.blender)
                mmod.connectAttr(blendNode.getOutput(), bindJnt.name+".rotate")

             
            # DELETING GUIDES
            mc.delete(legJnt, ankleGuide)


    def FK_setUp(self, legJNTList=[], parent=None):
        # GLOBALS
        resetJNTCount()
        resetTRNCount()
        # 1. CREATING HIERARCHY
        legFK_GRP = mmod.transform(side=self.side, name=self.legName+"FK", type="GRP", parent=parent)
        legFKJntGRP = mmod.transform(side=self.side, name=self.legName+"FK"+"Joints", type="GRP", parent=legFK_GRP)

        # 2.1. LEG JNT CHAIN
        jntChain = rigFn.createFKChain(legJNTList, side=self.side, name=self.legName+"FK", segmentList=self.legSegments, parent=legFKJntGRP)
        self.FKjntChain = jntChain

    def bindJnt_setUp(self, legJNTList=[], parent=None):
        # GLOBALS
        resetJNTCount()
        resetTRNCount()

        # 2.1. LEG JNT CHAIN
        jntChain = rigFn.createJntChain(legJNTList, side=self.side, name=self.legName+"Bind", segmentList=self.legSegments, parent=parent)
        self.bindJntChain = jntChain



    def IK_setUp(self, legJNTList=[], parent=None):

        ''' 
        1. HIERARCHY STRUCTURE
            legName+"IK"_GRP
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
            2.4. Pole vector
        '''
        # GLOBALS
        resetJNTCount()
        resetTRNCount()
        # 1. CREATING HIERARCHYma
        legIK_GRP = mmod.transform(side=self.side, name=self.legName+"IK", type="GRP", parent=parent)
        legIKJntGRP = mmod.transform(side=self.side, name=self.legName+"IK"+"Joints", type="GRP", parent=legIK_GRP)
        limitedAnkleGRP = mmod.transform(side=self.side, name=self.legName+"IK"+"LimitedAnkle", type="GRP", parent=legIK_GRP)
        ankleCtrl = rigFn.constructCTL(self.ankleGuide, side=self.side, name=self.legName+"IK"+"Ankle", parent=legIK_GRP, ctrlScale=mc.getAttr(legJNTList[2]+".radius"))
        ankleJNT = mc.listRelatives(ankleCtrl)[0]
        settingsGRP = mmod.transform(side=self.side, name=self.legName+"IK"+"Settings", type="GRP", parent=legIK_GRP)
        self.ankleCtrl = ankleCtrl
        self.footHook = limitedAnkleGRP
        # Position Ctrl
        fn.rotateShapePoints(ankleCtrl.name, rotationVector=[90, 0, 0], pivot=mc.xform(legJNTList[2], q=True, t=True, ws=True))

        # 2. SET UP
        # 2.1. LEG JNT CHAIN
        jntChain = rigFn.createJntChain(legJNTList, side=self.side, name=self.legName+"IK", segmentList=self.legSegments, parent=legIKJntGRP)
        self.IKjntChain=jntChain
        # 2.2. IK HANDLE
        ikHandle = rigFn.createIKHandle(jntChain[0], jntChain[len(jntChain)-1], side=self.side, name=self.legName+"IK"+"IKHandle", parent=limitedAnkleGRP)
        
        # ikHandle = rigFn.createIKHandle(jntChain[0], jntChain[len(jntChain)-1], side=side, name=self.legName+"IK"+"IKHandle")
        
        # 2.3. LIMITED IK
        # Settings GRP
        # Get bone length
        femurLength = mc.getAttr(fn.getParent(jntChain[1].name)+".translateX")
        tibiaLength = mc.getAttr(fn.getParent(jntChain[2].name)+".translateX")
        # String to worldMatrix Attr
        hipWorldMatrixAttr = jntChain[0].getWorldMatrix()
        # hipWorldMatrixValue = mc.getAttr(hipWorldMatrixAttr)
        # Add attr
        femurLengthAttr     = settingsGRP.addAttr( longName="femurLength", softMinValue=0, defaultValue=femurLength, softMaxValue=2*femurLength, attrType="double", keyable=True)
        tibiaLengthAttr     = settingsGRP.addAttr( longName="tibiaLength", softMinValue=0, defaultValue=tibiaLength, softMaxValue=2*tibiaLength, attrType="double", keyable=True)
        hipStartMatrixAttr  = settingsGRP.addAttr(longName="hipStartMatrix", attrType="matrix")
        mmod.connectAttr(hipWorldMatrixAttr, settingsGRP.name+".hipStartMatrix")
        mc.disconnectAttr(hipWorldMatrixAttr, settingsGRP.name+".hipStartMatrix")
        # mc.setAttr(hipWorldMatrixAttr, hipWorldMatrixValue, type="matrix")
        
        # Connect attr
        mmod.connectAttr(settingsGRP.name+".femurLength", fn.getParent(jntChain[1].name)+".translateX")
        mmod.connectAttr(settingsGRP.name+".tibiaLength", fn.getParent(jntChain[2].name)+".translateX")
        
        # AddDoubleLiniar: femour.len+tibia.len
        maxLength = mmod.addDoubleLinear(side=self.side, name="legMaxLength")
        mmod.connectAttr(settingsGRP.name+".femurLength", maxLength.getInput1())
        mmod.connectAttr(settingsGRP.name+".tibiaLength", maxLength.getInput2())
        
        # DecompMatrix: anlkeJNT.worldMatrix
        ankleWorldDecompose = mmod.decomposeMatrix(side=self.side, name="ankleWorldMatrix") 
        mmod.connectAttr(ankleJNT+".worldMatrix", ankleWorldDecompose.getInputMatrix())

        # DecompMatrix: hipStartMatrixAttr
        hipWorldMatrixDecompose = mmod.decomposeMatrix(side=self.side, name="hipWorldMatrix")
        mmod.connectPlugs(hipStartMatrixAttr, hipWorldMatrixDecompose.inputMatrix)

        # PlusMinusAverage: get the vector between the hip and the ankle
        ankleHipVecDir = mmod.plusMinusAverage(side=self.side, name="hipAngleVecDir")
        # Subtraction Operation
        ankleHipVecDir.operation = 2 
        mmod.connectAttr(ankleWorldDecompose.getOutputTranslate, ankleHipVecDir.name+".input3D[0]")
        mmod.connectAttr(hipWorldMatrixDecompose.getOutputTranslate, ankleHipVecDir.name+".input3D[1]")

        # VectorProduct: normalize hip ankle vector
        vectorNormalize = mmod.vectorProduct(side=self.side, name="hipAnkleVectorNormalize")
        vectorNormalize.operation = 0
        vectorNormalize.normalizeOutput = 1
        mmod.connectPlugs(ankleHipVecDir.output3D, vectorNormalize.input1)


        # DistanceBetween: hipStartMatrix and ankle( child of ankle_CTL)
        hipAnkleDist = mmod.distanceBetween(side=self.side, name="hipAnkle")
        mmod.connectPlugs(hipStartMatrixAttr, hipAnkleDist.inMatrix1)
        mmod.connectAttr(ankleJNT+".worldMatrix", hipAnkleDist.getInMatrix2())

        # Clamp: distance to max = length(femour.len+tibia.len)
        distancedClamp = mmod.clamp(side=self.side, name="hipAnkleDist")
        mmod.connectPlugs(hipAnkleDist.distance, distancedClamp.inputR)
        mmod.connectPlugs(maxLength.output, distancedClamp.maxR)

        # MultiplyDivide: ankleHipVecDir*ankleHipMaxLength  
        multiplyDivideNode = mmod.multiplyDivide(side=self.side, name="hipAnkleVector")
        mmod.connectAttr(vectorNormalize.getOutput(), multiplyDivideNode.getInput1())
        mmod.connectAttr(distancedClamp.getOutputR(), multiplyDivideNode.getInput2()+".input2X")
        mmod.connectAttr(distancedClamp.getOutputR(), multiplyDivideNode.getInput2()+".input2Y")
        mmod.connectAttr(distancedClamp.getOutputR(), multiplyDivideNode.getInput2()+".input2Z")

        # PlusMinusAverage: ankleHipVec in local space of hip
        plusNode = mmod.plusMinusAverage(side=self.side, name="localizeHipAnkleVector")
        mmod.connectAttr(multiplyDivideNode.getOutput(), plusNode.name+".input3D[0]")
        mmod.connectAttr(hipWorldMatrixDecompose.getOutputTranslate, plusNode.name+".input3D[1]")
        mmod.connectAttr(plusNode.name+".output3D", limitedAnkleGRP.name+".translate")

        # 2.4. POLE VECTOR CONSTRAINT
        poleCtrl = mmod.circle(side=self.side, name="poleVector", parent=legIK_GRP)
        # position ctrl
        fn.scaleShapePoints(poleCtrl.name, mc.getAttr(legJNTList[2]+".radius")*0.25)
        fn.snapTool(jntChain[1], poleCtrl)
        # mc.xform(poleCtrl, t=[0, 0, mc.getAttr(legJNTList[2]+".radius")], r=True)
        mc.makeIdentity(poleCtrl.name, a=True, t=True, r=True, s=True) 
        mc.delete(poleCtrl.name, ch=True)
        mc.poleVectorConstraint(poleCtrl.name, ikHandle)

        # # TEMP: FOR VISUALIZATION
        # cube = mc.polyCube(n="limitedAnkle", w=10, h=10, d=10)[0]
        # mc.parent (cube, limitedAnkleGRP)
        # mc.setAttr(cube+".translateX", 0)
        # mc.setAttr(cube+".translateY", 0)
        # mc.setAttr(cube+".translateZ", 0)
         

   

L_leg = leg(legJnt="L_legHip00_JNT", ankleGuide="L_legAnkleGuid00_LOC", side="L")
L_foot = foot(footJnt="L_footAnkle00_JNT", ankleCTL=L_leg.ankleCtrl, side="L", parent=L_leg.footHook)


R_leg = leg(legJnt="R_legHip00_JNT", ankleGuide="R_legAnkleGuid00_LOC", side="R")
R_foot = foot(footJnt="R_footAnkle00_JNT", ankleCTL=R_leg.ankleCtrl, side="R", parent=R_leg.footHook)
