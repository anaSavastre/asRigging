import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 

class foot(object):
    def __init__(self, side="C", footJnt=None, root=None, parent=None, hook=None):
        ''' 
        root = leg() object
        parent = parent bind jnt (FK foot)
        '''
        # self
        self.side = side
        self.footJnt = footJnt
        self.legRoot = root
        self.ankleCtrl = root.effectorCtrl
        self.parent = parent
        self.hook = hook
        self.footSegments = ["Ankle", "Tarsals", "Toes"]
        self.footName="foot"
        
        if (footJnt):
            # FK Foot            
            footJNTList = fn.descendentsList(root=footJnt)
            self.footJNTList = []
            for elem in footJNTList:
                self.footJNTList.append(elem)
        

            self.FKfoot_setUp(footJNTList=footJNTList, parent=self.parent)
            # FOOT ROLL
            self.footRoll_setUp(footJNTList=footJNTList, parent=root.segmentGRP)

            # CONSTRAINING FOOT TO  FK ANKLE (temporary done with orient constraint)
            orientConstraint =mc.orientConstraint(self.legRoot.FKjntChain[-1], fn.getParent(fn.getParent(self.footFKJnt[0])), mo=True)[0]
            ocWeightAlias = mc.orientConstraint(orientConstraint, q=True, wal=True)[0]
            mmod.connectAttr( self.legRoot.reverseBlend.getOutput(), orientConstraint+"."+ocWeightAlias)
            
            # Making Scaleable
            mmod.connectAttr(fn.getParent(self.hook)+".scale", fn.getParent(self.footFKJnt[0])+".scale")
            
            # 
            # DELETING GUIDES
            mc.delete(footJnt)


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

            5. CONNECT FOOTROLL TO FK FOOT 
                5.0. Get Heel Toe Vector (bind pose value)
                5.1. Get Ankle Tarsal Vector 
                5.2. Angle Between vectors
                5.3. Hook Foot GRP
                5.4. Hook Toes
        '''
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()
        # 0. CREATING HEEL JNT
        # Getting the plane defined by the guides
        # Getting the 3 points
        p1 = mc.xform(footJNTList[0], ws=True, q=True, t=True)
        p2 = mc.xform(footJNTList[1], ws=True, q=True, t=True)
        p3 = mc.xform(footJNTList[2], ws=True, q=True, t=True)
        plane = fn.planeEquation(p1, p2, p3)
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
        self.animParameters = animParameters
        # 2.0. Creating Joints
        footJNTList.append(heelJnt)
        footJNTList.reverse()
        segments = self.footSegments
        segments.append("Heel")
        segments.reverse()
        newGuides = rigFn.jntHierarchy(footJNTList)
        footRolljnt = rigFn.createJntChain(newGuides, side=self.side, name=self.footName+"Roll", segmentList = segments, parent=jointsGrp)
        self.footRollJnt = footRolljnt
        mc.delete(newGuides)
        # 2.1. Creating control attr
        footRoll = animParameters.addAttr(longName="footRoll", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        tarsalLock = animParameters.addAttr(longName="tarsalLock", softMinValue=-1.7, defaultValue=0.34, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        straighten = animParameters.addAttr(longName="straighten", softMinValue=-15, defaultValue=1.5, softMaxValue=15, attrType="double", keyable=True)
        self.footRoll = footRoll
        self.tarsalLock = tarsalLock
        self.straighten = straighten
        toeRest = configParameters.addAttr( longName="toeRest", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        tarsalRest = configParameters.addAttr( longName="tarsalRest", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)

        mc.setAttr(configParameters.name+".toeRest", mc.getAttr(fn.getParent(footRolljnt[1].name)+".rotateZ"))
        mc.setAttr(configParameters.name+".tarsalRest", mc.getAttr(fn.getParent(footRolljnt[2].name)+".rotateZ"))
        # 2.2. Linking control Attr
        mmod.connectAttr(configParameters.name+".toeRest", fn.getParent(footRolljnt[1].name)+".rotateZ")
        mmod.connectAttr(configParameters.name+".tarsalRest",fn.getParent(footRolljnt[2].name)+".rotateZ")

        # 3. FOOT ROLL NETWORK
        # 3.0. HEEL BACK ROTATION
        clampHeel = mNode.clamp(side=self.side, name="footRoll"+"footRollHeel")
        mmod.connectPlugs(footRoll, clampHeel.inputR)
        mc.setAttr(clampHeel.name+".minR", -100)
        inverseMult =mNode.multDoubleLinear(side=self.side, name="footRoll"+"footRollHeel")
        mmod.connectPlugs(clampHeel.outputR, inverseMult.input1)
        mc.setAttr(inverseMult.name+".input2", -1)
        mmod.connectPlugs(inverseMult.output, footRolljnt[0].rotateZ)
        # 3.1. TARSAL ROTATION
        clampTarsalRot = mNode.clamp(side=self.side, name="footRoll"+"footRollTarsalRotation")
        clampTarsalLock = mNode.clamp(side=self.side, name="footRoll"+"footRollTarsalLock")
        mmod.connectPlugs(tarsalLock, clampTarsalLock.inputR)
        mc.setAttr(clampTarsalLock.getMaxR(), 100)
        mmod.connectPlugs(footRoll, clampTarsalRot.inputR)
        mmod.connectPlugs(clampTarsalLock.outputR, clampTarsalRot.maxR)
        # 3.2. STRAIGHTENING
        diffRollTarsalLock = mNode.plusMinusAverage(side=self.side, name="footRoll"+"toeRotation")
        clampDiff = mNode.clamp(side=self.side, name="footRoll"+"toeRotation")
        mc.setAttr(diffRollTarsalLock.getOperation(), 2)
        mmod.connectAttr(animParameters.name+".footRoll", diffRollTarsalLock.name+".input1D[0]")
        mmod.connectAttr(clampTarsalLock.getOutputR(), diffRollTarsalLock.name+".input1D[1]")
        mmod.connectAttr(diffRollTarsalLock.name+".output1D", clampDiff.getInputR())
        mc.setAttr(clampDiff.getMaxR(), 100)
        mmod.connectPlugs(clampDiff.outputR, footRolljnt[1].rotateZ)

        # Subtracting this rotation from the tarsal Rot
        invClampDiff = mNode.multDoubleLinear(side=self.side, name="footRoll"+"invToeRotation")
        straightenCoef = mNode.multDoubleLinear(side=self.side, name="footRoll"+"straightenCoef")
        addStraightening = mNode.addDoubleLinear(side=self.side, name="footRoll"+"tarsalRotation")
        mc.setAttr(invClampDiff.getInput2(), -1)
        mmod.connectPlugs(clampDiff.outputR, invClampDiff.input1)
        mmod.connectPlugs(invClampDiff.output, straightenCoef.input1)
        mmod.connectAttr(animParameters.name+".straighten", straightenCoef.getInput2())

        mmod.connectPlugs(straightenCoef.output, addStraightening.input1)
        mmod.connectAttr(clampTarsalRot.getOutputR(), addStraightening.getInput2())

        mmod.connectPlugs(addStraightening.output, footRolljnt[2].rotateZ)

        
        # 4. CONNECT FOOTROLL TO LEG
        # Get Ankle jnt WM Translation
        decompMtxFootRollAnkle = mNode.decomposeMatrix(side=self.side, name="footRoll"+"footRollAnkle")
        decompMtxAnkeCtl = mNode.decomposeMatrix(side=self.side, name="footRoll"+"ankleControl")
        subtractingTransformations = mNode.plusMinusAverage(side=self.side, name="footRoll"+"totalTransforms")
        mmod.connectAttr(footRolljnt[3].name+".worldMatrix", decompMtxFootRollAnkle.name+".inputMatrix") 
        mmod.connectAttr(self.ankleCtrl.name+".worldMatrix", decompMtxAnkeCtl.name+".inputMatrix")
        mc.disconnectAttr(self.ankleCtrl.name+".worldMatrix", decompMtxAnkeCtl.name+".inputMatrix")
        mmod.connectAttr(decompMtxFootRollAnkle.getOutputTranslate(), subtractingTransformations.name+".input3D[0]")
        mmod.connectAttr(decompMtxAnkeCtl.getOutputTranslate(), subtractingTransformations.name+".input3D[1]")
        mc.setAttr(subtractingTransformations.getOperation(), 2)
        mmod.connectAttr(subtractingTransformations.getOutput3D(), mc.listRelatives(self.ankleCtrl, c=True)[1] +".translate")


        # # 5. CONNECT FOOTROLL TO FK FOOT (WITH CONSTRAINTS)
        # 5.0. DUPLICATING FK FOOT
        localFKGrp = mmod.transform(side=self.side, name="footRoll"+"LocalFK", parent=jointsGrp)
        localFkJnt = rigFn.createJntChain(self.footJNTList, side=self.side, name="footRoll"+"LocalFK", segmentList=self.footSegments, parent=localFKGrp)
        # 5.1. ORIENT CONSTRAINT OFS GRPs
        toeOrientConstraint = mc.orientConstraint(footRolljnt[1].name, fn.getParent(localFkJnt[1].name), mo=True)[0]
        tarsalOrientConstraint = mc.orientConstraint(footRolljnt[2].name, fn.getParent(localFkJnt[0].name), mo=True)[0]
        # 5.2. SET INFLUENCES TO BE ACTIVE JUST IN IK MODE
        weight = mc.orientConstraint(toeOrientConstraint, q=True, wal=True)[0]
        mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", toeOrientConstraint+"."+weight)
        weight = mc.orientConstraint(tarsalOrientConstraint, q=True, wal=True)[0]
        mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", tarsalOrientConstraint+"."+weight)
        # 5.3. CONNECTING ROTATION TO FK OFS GRPs
        mmod.connectAttr(fn.getParent(localFkJnt[1].name)+".rotate", fn.getParent(self.footFKJnt[1].name)+".rotate")
        mmod.connectAttr(fn.getParent(localFkJnt[0].name)+".rotate", fn.getParent(self.footFKJnt[0].name)+".rotate")
        # 5.4. HIDING GRP
        mc.hide(localFKGrp)
        # 6. Connecting FootRoll to leg Ctrl
        mmod.connectPlugs(self.legRoot.footRollAttr, self.footRoll)

        # DELETING GUIDS
        mc.delete(heelJnt)


    def FKfoot_setUp(self, footJNTList=[], parent=None):
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()
        # 1. CREATING HIERARCHY
        footFK_GRP = mmod.transform(side=self.side, name=self.footName+"FK", type="GRP", parent=parent)
        mc.setAttr(footFK_GRP.name+".inheritsTransform", 0)
        footFKJntGRP = mmod.transform(side=self.side, name=self.footName+"FK"+"Joints", type="GRP", parent=footFK_GRP)
        # 2.1. CONSTRAINING FOOT TO  IK ANKLE
        decmpMatrixLimAnkle = mNode.decomposeMatrix(side=self.side, name="limitedAnkleWM")
        decmpMatrixFKAnkle = mNode.decomposeMatrix(side=self.side, name="FKAnkleWM")
        conditionNode = mNode.condition(side=self.side, name="legBlendMode")
        mmod.connectAttr(self.legRoot.limitedEffector.name+".worldMatrix", decmpMatrixLimAnkle.getInputMatrix())
        mmod.connectAttr(self.legRoot.FKjntChain[2].name+".worldMatrix", decmpMatrixFKAnkle.getInputMatrix())
        mmod.connectAttr(decmpMatrixLimAnkle.getOutputTranslate(), conditionNode.getColorIfFalse())
        mmod.connectAttr(decmpMatrixFKAnkle.getOutputTranslate(), conditionNode.getColorIfTrue())
        mmod.connectPlugs(self.legRoot.blendAttr, conditionNode.firstTerm)
        mmod.connectPlugs(conditionNode.outColor, footFKJntGRP.translate)
    
        # 2.2. FOOT JNT CHAIN
        jntChain = rigFn.createFKChain(footJNTList, side=self.side, name=self.footName+"FK", segmentList=self.footSegments, parent=footFKJntGRP)
        self.footFKJnt = jntChain
        self.footFKGRP = footFKJntGRP.name

        # MATCHING GLOBAL ORIENTATION
        decomMatrix = mNode.decomposeMatrix(side=self.side, name="rootGlobalTransformations")
        mmod.connectAttr(self.hook.name+".worldMatrix", decomMatrix.getInputMatrix())
        mmod.connectAttr(decomMatrix.getOutputRotate(), footFKJntGRP.name+".rotate")
  
