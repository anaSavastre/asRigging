import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import controlFn as ctlFn

          
class blendFKIK(object):
    def __init__(self, side, jnt = None, name="segment", segmentsList=["base", "midPoint", "effector"], parent=None, root=None, hook=None):
        '''
        
        VARIABLES
        side =system side (C, L, R)
        jnt = guideJnt (first jnt in chain)
        name = name
        segments ={baseSegment, midSegment, effector} (default values)
        parent = rig set-up location (exp: rigGRP)
        root = location of bind jnts
        hook = rig rootJnt (CharacterControl) (for parnenting: ankle and poleVectorCtrl)
        
        NAMES
        

        1. IK SET-UP
        2. FK SET-UP
        3. FK IK BLEND

        '''

        # self
        self.side = side
        self.jntGuide = jnt
        
        self.parent = parent
        self.root = root
        self.hook = hook
        self.segments = segmentsList
        self.name=name

        
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()

        # SET_UP
        if (jnt!=None):
            self.jntGuideList = fn.descendentsList(root=self.jntGuide)
            self.controllerGuide = self.jntGuideList[-1]
            if (len(self.jntGuideList)>3):
                self.jntGuideList=self.jntGuideList[0:3]
            segment_GRP = mmod.transform(side=side, name=self.name, type="GRP", parent=parent)
            self.segmentGRP = segment_GRP

            # IK 
            self.IK_setUp(jntList=self.jntGuideList, parent=segment_GRP)

            # FK 
            self.FK_setUp(jntList=self.jntGuideList, parent=segment_GRP) 

            # Bind jnt
            self.bindJnt_setUp(jntList=self.jntGuideList, parent=self.root) 

            # Creating settingsCtrl
            self.settingsCtrlSetUp(jntList=self.jntGuideList, parent=self.bindJntChain[2])
            
            # Creating stretchyLimbs
            self.stretchyLimbsSetUp()
           
            for ikJnt, fkJnt, bindJnt, segment in zip(self.IKjntChain, self.FKjntChain, self.bindJntChain, self.segments):

                #########################################################################################################################################################
               
                # ######## BLEND NODE VERSION ########
                # blendNode = mNode.blendColors(side=self.side, name=segment+"FK_IK", type ="BLD")
                # mmod.connectAttr(fkJnt.name+".rotate", blendNode.getColor2())
                # mmod.connectAttr(ikJnt.name+".rotate", blendNode.getColor1())
                # mmod.connectPlugs(self.blendAttr, blendNode.blender)
                # mmod.connectAttr(blendNode.getOutput(), bindJnt.name+".rotate")
                # # Visibility
                # mmod.connectPlugs(self.blendAttr, self.IKGRP.visibility)
                # try :
                #     mmod.connectAttr(self.reverseBlend.getOutput(), self.FKjntChain[0].name+".visibility")
                # except:
                #     self.reverseBlend = mNode.addDoubleLinear(side = self.side, name="inverseFKIKBlend")
                #     mmod.connectPlugs(self.blendAttr, self.reverseBlend.input1)
                #     mc.setAttr(self.reverseBlend.getInput2(), -1)
                #     mmod.connectAttr( self.reverseBlend.getOutput(), self.FKjntChain[0].name+".visibility")
                # ######## BLEND NODE VERSION ########

                #########################################################################################################################################################
                #########################################################################################################################################################


                ######## Parent CONSTRAINT VERSION ########
                # Orient Constraint
                fkParentConstraint = mc.parentConstraint(fkJnt, bindJnt)[0]
                ikParentConstraint = mc.parentConstraint(ikJnt, bindJnt)[0]
                
                # Getting weight Alias
                fkWeightAlias = mc.parentConstraint(fkParentConstraint, q=True, wal=True)[0]
                ikWeightAlias = mc.parentConstraint(ikParentConstraint, q=True, wal=True)[1]
                # Making Connections

                # FK
                # Reverse Node
                try:
                    mmod.connectAttr(self.reverseBlend.getOutput(), fkParentConstraint+"."+fkWeightAlias)
                    mmod.connectAttr( self.reverseBlend.getOutput(), self.FKjntChain[0].name+".visibility")
            
                except:
                    self.reverseBlend = mNode.addDoubleLinear(side = self.side, name="inverseFKIKBlend")
                    mmod.connectPlugs(self.blendAttr, self.reverseBlend.input1)
                    mc.setAttr(self.reverseBlend.getInput2(), -1)
                    mmod.connectAttr(self.reverseBlend.getOutput(), self.FKjntChain[0].name+".visibility")
                    mmod.connectAttr(self.reverseBlend.getOutput(), fkParentConstraint+"."+fkWeightAlias)            
                
                # IK
                mmod.connectAttr(self.settingCtl.name+".fkIkBlend", ikParentConstraint+"."+ikWeightAlias)
                mmod.connectPlugs(self.blendAttr, self.IKGRP.visibility)


                ######## ORIENT CONSTRAINT VERSION ########

                #########################################################################################################################################################

            # Hooking to Parent
            # 1. Making Start matrix relative to ROOT
            relativeMatrix = mmod.transform(side=self.side, name=self.name+"RelativeStratMatrix", parent=self.root)
            # Aligning with bindJnt[0]
            fn.align(self.bindJntChain[0], relativeMatrix)
            mmod.connectAttr(relativeMatrix.getWorldMatrix(), self.startMatrix)
            # 2. Parent constraint FK and IK jnts to ROOT
            if (root!=None):
                mmod.connectAttr(self.baseSegWorldMatrixDecompose.getOutputTranslate(), fn.getParent(self.FKjntChain[0])+".translate")
                mmod.connectAttr(self.baseSegWorldMatrixDecompose.getOutputTranslate(), fn.getParent(self.IKjntChain[0])+".translate")

                #mc.scaleConstraint(root, fn.getParent(fn.getParent(self.FKjntChain[0])), mo=True)
                #mc.scaleConstraint(root, fn.getParent(fn.getParent(self.IKjntChain[0])), mo=True)
         


            # DELETING GUIDES
            mc.delete(jnt)

    def stretchyLimbsSetUp(self):
        print "Stretchy Limbs"
        # Creating Nodes
        lengthDifference = mNode.plusMinusAverage(side=self.side, name="lenDiference")
        clampNode = mNode.clamp(side=self.side, name="clampLenDist")
        segmentLength = mNode.multDoubleLinear(side=self.side, name="segmentLenght")
        stretchyAttrMult = mNode.multDoubleLinear(side=self.side, name="stretchyAttr")
        addOriginalDistBase = mNode.addDoubleLinear(self.side, name="addOriginalLengthBase")
        addOriginalDistMid = mNode.addDoubleLinear(self.side, name="addOriginalLengthMid")

        # Delta Distance
        mmod.connectAttr(self.baseEndDistNode.getDistance(), lengthDifference.name+".input1D[0]")
        mc.setAttr(lengthDifference.name+".input1D[1]",  self.baseSegmentLength+self.midSegmentLength)
        lengthDifference.operation = 2
        # Clamp Distance
        mmod.connectAttr(lengthDifference.name+".output1D", clampNode.getInputR())
        clampNode.maxR = 1000000
        # Dividing Length in Segments
        mmod.connectAttr(clampNode.getOutputR(), segmentLength.getInput1())
        segmentLength.input2 = 0.5
        # Multiply by the StretchLimbs Attribute
        mmod.connectAttr(segmentLength.getOutput(), stretchyAttrMult.getInput1())
        mmod.connectAttr(self.settingCtl.name+".stretchyLimb", stretchyAttrMult.getInput2())
        # Adding To Original Length
        mmod.connectAttr(stretchyAttrMult.getOutput(), addOriginalDistBase.getInput1())
        mmod.connectAttr(stretchyAttrMult.getOutput(), addOriginalDistMid.getInput1())
        mc.setAttr(addOriginalDistBase.getInput2(), self.baseSegmentLength)
        mc.setAttr(addOriginalDistMid.getInput2(), self.midSegmentLength)
        # Connect To Segment Length
        mmod.connectAttr(addOriginalDistBase.getOutput(), self.settingsGRP.name+"."+self.segments[0]+"Length")
        mmod.connectAttr(addOriginalDistMid.getOutput(), self.settingsGRP.name+"."+self.segments[1]+"Length") 


    def settingsCtrlSetUp(self, jntList=[], parent=None):
        settingsCtrlGrp = mmod.transform(side=self.side, name=self.name+"Settings", parent=self.bindJntChain[2] )
        # Position Group
        pozZ = mc.xform(settingsCtrlGrp, ws=True, q=True, t=True)[2]
        grpSign = 1 if pozZ>0 else -1
        guideJntRad = mc.getAttr(jntList[2]+".radius")
        pozZ = grpSign*(abs(pozZ)+guideJntRad) *0.4
        # mc.xform(settingsCtrlGrp, t=[poxZ, 0, 0], r=True)
        # Creating CTRL
        self.settingCtl = ctlFn.settingCtl(side=self.side, name=self.name+"Settings")#, parent=settingsCtrlGrp)
        mc.parent (self.settingCtl, settingsCtrlGrp)
    
        mc.setAttr(self.settingCtl.name+".translateX",0)
        mc.setAttr(self.settingCtl.name+".translateY",0)
        mc.setAttr(self.settingCtl.name+".translateZ",0)
        mc.setAttr(self.settingCtl.name+".rotateX",0)
        mc.setAttr(self.settingCtl.name+".rotateY",0)
        mc.setAttr(self.settingCtl.name+".rotateZ",0)


        # Scaling CTRL
        fn.scaleShapePoints(self.settingCtl.name, mc.getAttr(jntList[2]+".radius")*0.6)
        fn.rotateShapePoints(self.settingCtl.name, rotationVector=[0, 90, 0], pivot=mc.xform(self.settingCtl.name, q=True, t=True, ws=True))

        fn.translateShapePoints(self.settingCtl.name, [0, 0, pozZ], 0)
    
        # Creating attribute on ctrl
        self.blendAttr = self.settingCtl.addAttr(longName="fkIkBlend", softMinValue=0, defaultValue=1, softMaxValue=1, attrType="short", keyable=True)
        self.stretchyLimbs = self.settingCtl.addAttr(longName="stretchyLimb", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short", keyable=True)
        


    
    def bindJnt_setUp(self, jntList=[], parent=None):
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()

        # 2.1. LEG JNT CHAIN
        jntChain = rigFn.createJntChain(jntList, side=self.side, name="bind"+self.name.capitalize(), segmentList=self.segments, parent=parent)
        self.bindJntChain = jntChain
    
    def FK_setUp(self, jntList=[], parent=None):
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()
        # 1. CREATING HIERARCHY
        FK_GRP = mmod.transform(side=self.side, name=self.name+"FK", type="GRP", parent=parent)
        FKJntGRP = mmod.transform(side=self.side, name=self.name+"FK"+"Joints", type="GRP", parent=FK_GRP)

        # 2.1. ARM JNT CHAIN
        jntChain = rigFn.createFKChain(jntList, side=self.side, name=self.name+"FK", segmentList=self.segments, parent=FKJntGRP)
        self.FKjntChain = jntChain

        
    def IK_setUp(self, jntList=[], parent=None):

        ''' 
        1. HIERARCHY STRUCTURE
            name+"IK"_GRP
                > Settings_GRP: addAttr(length01, length12...)
                > Joints_GRP    
                        baseSegment_GRP>OFS>JNT
                            midSegment_GRP>OFS>CTL>JNT
                                effector_GRP>OFS>CTL>JNT
                > effectorCtrl_GRP>OFS>CTL
                > limitedEffector_GRP
                        cube (temp for testing)
                        footJointsGRP>>>>
                        IKHandle

        2. SET UP
            2.1. Creating joints form guides
            2.2. Creating IK Handle
            2.3. Limited effector set-up
            2.4. Pole vector
        '''
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()
        # 1. CREATING HIERARCHY
        IK_GRP = mmod.transform(side=self.side, name=self.name+"IK", type="GRP", parent=parent)
        IKJntGRP = mmod.transform(side=self.side, name=self.name+"IK"+"Joints", type="GRP", parent=IK_GRP)
        limitedEffectorGRP = mmod.transform(side=self.side, name=self.name+"IK"+"Limited"+self.segments[-1], type="GRP", parent=IK_GRP)
        effectorCtrl = rigFn.constructCTL(self.controllerGuide, side=self.side, name=self.name+"IK"+self.segments[-1], parent=IK_GRP, ctrlScale=mc.getAttr(jntList[2]+".radius"))
        fn.rotateShapePoints(effectorCtrl.name, rotationVector=[0, 90, 0], pivot=mc.xform(self.controllerGuide, q=True, ws=True, t=True))

        # Constraining Effector to rig Root
        mc.parentConstraint(self.hook.name, fn.getParent(fn.getParent(effectorCtrl.name)), mo=True)
        mmod.connectAttr(fn.getParent(self.hook.name)+".scale", fn.getParent(fn.getParent(effectorCtrl.name))+".scale")
        # mc.scaleConstraint(self.hook.name, fn.getParent(fn.getParent(effectorCtrl.name)), mo=True)
        effectorJNT = mc.listRelatives(effectorCtrl)[1]
        settingsGRP = mmod.transform(side=self.side, name=self.name+"IK"+"Settings", type="GRP", parent=IK_GRP)
        self.IKGRP = IK_GRP
        self.effectorCtrl = effectorCtrl
        self.limitedEffector = limitedEffectorGRP
        self.settingsGRP = settingsGRP
        # Position Ctrl
        fn.rotateShapePoints(effectorCtrl.name, rotationVector=[90, 0, 0], pivot=mc.xform(jntList[2], q=True, t=True, ws=True))

        # 2. SET UP
        # 2.1.  JNT CHAIN
        jntChain = rigFn.createJntChain(jntList, side=self.side, name=self.name+"IK", segmentList=self.segments, parent=IKJntGRP)
        self.IKjntChain=jntChain
        # 2.2. IK HANDLE
        ikHandle = rigFn.createIKHandle(jntChain[0], jntChain[len(jntChain)-1], side=self.side, name=self.name+"IK"+"IKHandle", parent=limitedEffectorGRP)
        self.ikHandle = ikHandle       
        # 2.3. LIMITED IK
        # Settings GRP
        # Get bone length
        baseSegmentLength = mc.getAttr(fn.getParent(jntChain[1].name)+".translateX")
        midSegmentLength = mc.getAttr(fn.getParent(jntChain[2].name)+".translateX")
        self.baseSegmentLength = baseSegmentLength
        self.midSegmentLength = midSegmentLength
        # String to worldMatrix Attr
        baseSegmentWMAttr = jntChain[0].getWorldMatrix()
        # baseSegmentWorldMatrixValue = mc.getAttr(baseSegmentWMAttr)
        # Add attr
        baseSegmentLengthAttr     = settingsGRP.addAttr( longName=self.segments[0]+"Length", softMinValue=0, defaultValue=baseSegmentLength, softMaxValue=2*baseSegmentLength, attrType="double", keyable=True)
        midSegmentLengthAttr     = settingsGRP.addAttr( longName=self.segments[1]+"Length", softMinValue=0, defaultValue=midSegmentLength, softMaxValue=2*midSegmentLength, attrType="double", keyable=True)
        baseSegmentStartMatrixAttr  = settingsGRP.addAttr(longName=self.segments[0]+"StartMatrix", attrType="matrix")
        self.startMatrix = settingsGRP.name+"."+self.segments[0]+"StartMatrix"
        mmod.connectAttr(baseSegmentWMAttr, settingsGRP.name+"."+self.segments[0]+"StartMatrix")
        mc.disconnectAttr(baseSegmentWMAttr, settingsGRP.name+"."+self.segments[0]+"StartMatrix")
        

        # Multiplying Length by Scaling Factor (in Y axis)
        multBaseLength = mNode.multDoubleLinear(side=self.side, name=self.segments[0]+"GlobalLength")
        multMidLength = mNode.multDoubleLinear(side=self.side, name=self.segments[1]+"GlobalLength")
        mmod.connectAttr(settingsGRP.name+"."+self.segments[0]+"Length", multBaseLength.getInput1())
        mmod.connectAttr(settingsGRP.name+"."+self.segments[1]+"Length", multMidLength.getInput1())
        mmod.connectAttr(fn.getParent(self.hook.name)+".scaleY", multBaseLength.getInput2())
        mmod.connectAttr(fn.getParent(self.hook.name)+".scaleY", multMidLength.getInput2())
        
        # Connect attr
        mmod.connectAttr(multBaseLength.getOutput(), fn.getParent(jntChain[1].name)+".translateX")
        mmod.connectAttr(multMidLength.getOutput(), fn.getParent(jntChain[2].name)+".translateX")
        
        # AddDoubleLiniar: baseSegment.len+midSegment.len
        maxLength = mNode.addDoubleLinear(side=self.side, name="MaxLength")
        mmod.connectAttr(multBaseLength.getOutput(), maxLength.getInput1())
        mmod.connectAttr(multMidLength.getOutput(), maxLength.getInput2())
        
        # DecompMatrix: effectorJNT.worldMatrix
        effectorWorldDecompose = mNode.decomposeMatrix(side=self.side, name=self.segments[2]+"WorldMatrix") 
        mmod.connectAttr(effectorJNT+".worldMatrix", effectorWorldDecompose.getInputMatrix())

        # DecompMatrix: baseSegmentStartMatrixAttr
        self.baseSegWorldMatrixDecompose = mNode.decomposeMatrix(side=self.side, name=self.segments[0]+"WorldMatrix")
        mmod.connectPlugs(baseSegmentStartMatrixAttr, self.baseSegWorldMatrixDecompose.inputMatrix)

        # PlusMinusAverage: get the vector between the baseSegment and the effector
        baseEffectorVecDir = mNode.plusMinusAverage(side=self.side, name=self.segments[0]+self.segments[2].capitalize()+"VecDir")
        # Subtraction Operation
        baseEffectorVecDir.operation = 2 
        mmod.connectAttr(effectorWorldDecompose.getOutputTranslate(), baseEffectorVecDir.name+".input3D[0]")
        mmod.connectAttr(self.baseSegWorldMatrixDecompose.getOutputTranslate(), baseEffectorVecDir.name+".input3D[1]")

        # VectorProduct: normalize baseSegment effector vector
        vectorNormalize = mNode.vectorProduct(side=self.side, name=self.segments[0]+self.segments[2].capitalize()+"VectorNormalize")
        vectorNormalize.operation = 0
        vectorNormalize.normalizeOutput = 1
        mmod.connectPlugs(baseEffectorVecDir.output3D, vectorNormalize.input1)


        # DistanceBetween: baseSegmentStartMatrix and effector( child of effector_CTL)
        baseEndDist = mNode.distanceBetween(side=self.side, name=self.segments[0]+self.segments[2].capitalize()+"Dist")
        mmod.connectPlugs(baseSegmentStartMatrixAttr, baseEndDist.inMatrix1)
        mmod.connectAttr(effectorJNT+".worldMatrix", baseEndDist.getInMatrix2())
        self.baseEndDistNode = baseEndDist
        # self.effectorCtrl
        # Clamp: distance to max = length(baseSegment.len+midSegment.len)
        distancedClamp = mNode.clamp(side=self.side, name="baseEndDist")
        mmod.connectPlugs(baseEndDist.distance, distancedClamp.inputR)
        # Checking if "maxLength.output" is negative
        if (mc.getAttr(maxLength.getOutput())<0):
            # Creating multiply node
            reverseNode = mNode.multDoubleLinear(side=self.side, name="absoluteLength")
            reverseNode.input2 = -1
            mmod.connectAttr(maxLength.getOutput(), reverseNode.getInput1())
            mmod.connectAttr(reverseNode.getOutput(), distancedClamp.getMaxR())
        else:
            mmod.connectPlugs(maxLength.output, distancedClamp.maxR)

        # MultiplyDivide: baseEffectorVecDir*effectorHipMaxLength  
        multiplyDivideNode = mNode.multiplyDivide(side=self.side, name=self.segments[0]+self.segments[2].capitalize()+"Vect")
        mmod.connectAttr(vectorNormalize.getOutput(), multiplyDivideNode.getInput1())
        mmod.connectAttr(distancedClamp.getOutputR(), multiplyDivideNode.getInput2()+".input2X")
        mmod.connectAttr(distancedClamp.getOutputR(), multiplyDivideNode.getInput2()+".input2Y")
        mmod.connectAttr(distancedClamp.getOutputR(), multiplyDivideNode.getInput2()+".input2Z")

        # PlusMinusAverage: effectorHipVec in local space of baseSegment
        plusNode = mNode.plusMinusAverage(side=self.side, name="loc"+self.segments[0]+self.segments[2].capitalize()+"Vect")
        mmod.connectAttr(multiplyDivideNode.getOutput(), plusNode.name+".input3D[0]")
        mmod.connectAttr(self.baseSegWorldMatrixDecompose.getOutputTranslate(), plusNode.name+".input3D[1]")
        mmod.connectAttr(plusNode.name+".output3D", limitedEffectorGRP.name+".translate")

        # 2.4. POLE VECTOR CONSTRAINT
        poleVectGlobal = mmod.transform(side=self.side, name=self.name+"PoleVectorGlobal", type="GRP", parent=IK_GRP)
        # Position Global Grp
        # Get X on plane defined by joints
        # Getting the plane defined by the guides
        # Getting the 3 points
        p1 = mc.xform(jntChain[0], ws=True, q=True, t=True)
        p2 = mc.xform(jntChain[1], ws=True, q=True, t=True)
        p3 = mc.xform(jntChain[2], ws=True, q=True, t=True)
        plane = fn.planeEquation(p1, p2, p3)
        
        # Finding x of poleVectGlobal grp
        y = mc.xform(jntChain[1], ws=True, q=True, t=True)[1]
        offset = mc.xform(jntChain[1].name, ws=True, q=True, t=True)[2]-mc.xform(jntChain[0].name, ws=True, q=True, t=True)[2]
        z = mc.xform(jntChain[1], ws=True, q=True, t=True)[2]+((offset+1)*mc.getAttr(self.jntGuideList[1]+".radius"))
        x = -(plane[3] + plane[2]*z + plane[1]*y)/plane[0]
        mc.xform(poleVectGlobal, t=[x, y, z], ws=True)

        
        poleVectGrp = mmod.transform(side=self.side, name=self.name+"PoleVector", type="GRP", parent=poleVectGlobal)
        poleCtrl =ctlFn.diamondControl(side=self.side, name=self.name+"PoleVector", parent=poleVectGrp)
        # Creating Aiming Curve
        # curve -d 1 -p 1 0 13 -p 0 0 -23 -k 0 -k 1 ;
        aimCUrveName = self.side+"_"+self.name+"PoleVectorAim"+"_CTL"
        aimCurve = mc.curve(p=[(0, 0, -10), (0, 0, 10)], d=1)
        mc.rename(aimCurve, aimCUrveName)
        # Parenting Shape
        aimCtrlShape = fn.getChildren(aimCUrveName)[0]
        mc.parent(aimCtrlShape, poleCtrl, s=True, r=True)
        mc.delete(aimCUrveName)
        # Constraining Curve Points
        # Knee Point
        localSpace = mNode.multMatrix(side=self.side, name="poleVectorLocalSpace")
        decompMatrix = mNode.decomposeMatrix(side=self.side, name="poleVectLocalSpace")
        mmod.connectAttr(self.IKjntChain[1].name+".worldMatrix", localSpace.name+".matrixIn[0]")
        mmod.connectAttr(poleCtrl.name+".worldInverseMatrix", localSpace.name+".matrixIn[1]")
        mmod.connectAttr(localSpace.getMatrixSum(), decompMatrix.getInputMatrix())
        mmod.connectAttr(decompMatrix.getOutputTranslate(), aimCtrlShape+".controlPoints[0]")
        # Controller Point
        mmod.connectAttr(fn.getChildren(poleCtrl)[0]+".controlPoints[8]", aimCtrlShape+".controlPoints[1]")

        # position ctrl
        fn.scaleShapePoints(poleCtrl.name, mc.getAttr(jntList[2]+".radius")*0.25)
        
        mc.delete(poleCtrl.name, ch=True)
        mc.poleVectorConstraint(poleCtrl.name, ikHandle)

        # Aim Constraint: Ctrl Alwais Oriented towarsd JNT
        # Creating obj parented to jnt
        aimObj = mmod.transform(side=self.side, name=self.name+"AimObj", type="GRP", parent=self.IKjntChain[1])
      
        # Constraining Control to Hook
        mc.parentConstraint(self.hook.name, poleVectGlobal.name, mo=True)

