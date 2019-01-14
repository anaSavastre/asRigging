''' 
Ana Maria Savastre
Bournemouth University 

Master Class Assignment: Frontier Rigging 

Character: Spinosaurus


'''

import maya.cmds as mc
import loadFn 
import socket



# TEMP
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import mayaNode as node
import asNodes as asNode
import controlFn as ctlFn



# Body Modules
import spineModule as spineMod
import neckModule as neckMod
import armModule as armMod
import scapulaModule as scapulaMod
import legModule as legMod
import footModule as footMod
import tailModule as tailMod
import handModule as handMod

# Face Module
import jawModule as jawMod
# GLOBALS
hostName = socket.gethostname()

if (hostName == "DESKTOP-4NJ3EJ0"):
    projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-CM0E2QL"):
    projectEnv = "C:/Users/Kari Noriy/Desktop/Ana/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-PQV0HOV"):
    projectEnv = "C:/Users/AnaMaria/Documents/asRigging/projects/masterClass/"

 
  

def resetLegMod():
    leg.rigParent = None



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
            self.FKfoot_setUp(footJNTList=footJNTList, parent=self.parent)
            # FOOT ROLL
            self.footRoll_setUp(footJNTList=footJNTList, parent=root.segmentGRP)

            # CONSTRAINING FOOT TO  FK ANKLE (temporary done with orient constraint)
            orientConstraint =mc.orientConstraint(self.legRoot.FKjntChain[-1], fn.getParent(self.footFKJnt[0]), mo=True)[0]
            ocWeightAlias = mc.orientConstraint(orientConstraint, q=True, wal=True)[0]
            mmod.connectAttr( self.legRoot.reverseBlend.getOutput(), orientConstraint+"."+ocWeightAlias)


            # # CONSTRAINING FOOT TO  IK ANKLE (temporary done with orient constraint)
            # orientConstraint =mc.orientConstraint(self.legRoot.IKjntChain[-1], fn.getParent(self.footFKJnt[0]), mo=True)[0]
            # ocWeightAlias = mc.orientConstraint(orientConstraint, q=True, wal=True)[1]
            # mmod.connectAttr( self.legRoot.effectorCtrl.name+".fkIkBlend", orientConstraint+"."+ocWeightAlias)
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


        # 5. CONNECT FOOTROLL TO FK FOOT 
        # ROLL TOES > FK TARSAL
        tarsalOrientConstraint = mc.orientConstraint(footRolljnt[2].name, fn.getParent(fn.getParent(self.footFKJnt[0].name)), mo=True)[0]
        weight = mc.orientConstraint(tarsalOrientConstraint, q=True, wal=True)[0]
        mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", tarsalOrientConstraint+"."+weight)
        
        # 5.4. Hook Toes
        hook = fn.getParent(self.footFKJnt[1].name)
        animBlend = mNode.animBlendNodeAdditiveDA(side=self.side, name="footRoll"+"tarsalRotationX")
        mmod.connectPlugs(footRolljnt[2].rotateZ, animBlend.inputA)
        # mc.setAttr(animBlend.getWeightA(), -1)
        mc.setAttr(animBlend.getInputB(), mc.getAttr(hook+".rotateZ"))
        mmod.connectAttr(animBlend.getOutput(), hook+".rotateZ")

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

class spinosaurus(loadFn.rigSceneSetup):    
    character = "spinosaurus"

    def springSolverLeg(self, side="C"):
        # CREATING CUSTOM SPRING SOLVER FOR LEG
        # NEW ANKLE CTRL
        guideJnt = mmod.joint(side =side, name="tempJNt", parent=side+"_footFK_Tarsals01_JNT")
        mc.setAttr(guideJnt.name+".radius", 57.95)
        mc.parent(guideJnt.name, w=True)
        mc.setAttr(guideJnt.name+".jointOrientX", 0)
        mc.setAttr(guideJnt.name+".jointOrientY", 0)
        mc.setAttr(guideJnt.name+".jointOrientZ", 0)
        self.ankleCtrl = rigFn.constructCTL(guideJnt.name, side =side, name="ankle", parent=side+"_legIKAnkle03_GRP")
        # Deleting guidef
        mc.delete(guideJnt)
        # mc.parent(side+"_legIKAnkle04_OFS", ankleCtrl.name)
        # Rotate shape points 90
        fn.rotateShapePoints(self.ankleCtrl.name, rotationVector=[90, 0, 0], pivot=[0, 0, 0])
        # Hide original Ankle Ctrl
        mc.hide(self.m_leg.effectorCtrl)
        
        roolGuides =  mc.listRelatives(self.m_foot.footRollJnt[0], ad=True, type="joint")
        roolGuides.append(self.m_foot.footRollJnt[0])
        roolGuides.reverse()
        footJnt1 = rigFn.createJntChain(roolGuides, side =side, name="footRollDuplicate", segmentList=["Heel", "Toes", "Tarsal", "Ankle"], parent=None)
        mc.parent(fn.getParent(fn.getParent(footJnt1[0])), side+"_legIKAnkle03_GRP")
        globalEffectorAimGrp = mmod.transform(side =side, name="tarsalAimEffectorGlobalMove", parent=side+"_ankle010_GRP")
        
        aimEffectorObj = mmod.transform(side =side, name="tarsalAimAnkleObj", parent= self.m_leg.effectorCtrl)
        upEffectorObj = mmod.transform(side =side, name="tarsalUpAnkleObj", parent=self.m_leg.effectorCtrl)
        
        
        mc.parent(aimEffectorObj, upEffectorObj, globalEffectorAimGrp)
        mc.xform(upEffectorObj, t=[0, 0, 50], r=True)
        mc.makeIdentity([aimEffectorObj, upEffectorObj], a=True, t=True, r=True)

        mc.aimConstraint(aimEffectorObj, footJnt1[2], aim=[1, 0, 0], u=[0, 1, 0], worldUpType="object", worldUpObject=upEffectorObj,  mo=True)
        
        # CONNECTING ROTATION
        addNode = mNode.animBlendNodeAdditiveDA(side =side, name="aimAddRotation")
        mmod.connectAttr(side+"_footRolltarsalRotation0*_ADD.output", addNode.getInputA())
        mmod.connectAttr(footJnt1[2].name+".rotateZ", addNode.getInputB())       
        mmod.connectAttr(addNode.getOutput(), self.m_foot.footRollJnt[2].name+".rotateZ")    
        mmod.connectAttr(footJnt1[2].name+".rotateX", self.m_foot.footRollJnt[2].name+".rotateX")     
        mmod.connectAttr(footJnt1[2].name+".rotateY", self.m_foot.footRollJnt[2].name+".rotateY") 

        # LIMIT AIM GRP TRANSLATION
        # ANKLE CTRL
        clampAnkle = mNode.clamp(side =side, name="ankleTranslation")
        # PELVIS CTRL
        multPelvis =mNode.multiplyDivide(side =side, name="pelvisTranslation")
        clampPelvis = mNode.clamp(side =side, name="pelvisTranslation")
        # ADDING INFLUENCES
        addTranslation = mNode.plusMinusAverage(side =side, name="aimGlobalMove")
        # CONNECTIONS
        mmod.connectAttr(self.ankleCtrl.name+".translate", clampAnkle.getInput())
        mc.setAttr(clampAnkle.getMax(), 0, 100, 75, type="double3")
        mc.setAttr(clampAnkle.getMin(), 0, -50, -10, type="double3")
        mmod.connectAttr(self.m_spine.pelvisCtl.name+".translate", multPelvis.getInput1())
        mc.setAttr(multPelvis.getInput2(), 0.5, 0.5, 0.5, type="double3")
        mmod.connectAttr(multPelvis.getOutput(), clampPelvis.getInput())
        mc.setAttr(clampPelvis.getMax(), 0, 100, 100, type="double3")
        mc.setAttr(clampPelvis.getMin(), 0, -50, -100, type="double3")
        mmod.connectAttr(clampAnkle.name+".output", addTranslation.name+".input3D[0]")
        mmod.connectAttr(clampPelvis.name+".output", addTranslation.name+".input3D[1]")
        mmod.connectAttr(addTranslation.getOutput3D(), globalEffectorAimGrp.name+".translate")
        mmod.connectAttr(self.ankleCtrl.name+".translate", self.m_leg.effectorCtrl.name+".translate")

    def connectingAnkleTarsal(self, side="C"):
        # Tarsal FK Manipulated by Ankle CTRL
        # Create GRP on top of FK Tarsal CTRL
        connectionGrp = mmod.transform(side=side, name="footFKTarsalConnection", type="GRP", parent=fn.getParent(self.m_foot.footFKJnt[1]))
        mc.parent(self.m_foot.footFKJnt[1], connectionGrp)
        animBlend = mNode.animBlendNodeAdditiveDA(side=side, name="inverseRotationX")
        # Connecting Ankle to FK Tarsal
        mmod.connectAttr(self.ankleCtrl.name+".rotateX", animBlend.getInputA())
        animBlend.weightA = -1
        mmod.connectAttr(animBlend.getOutput(), connectionGrp.name+".rotateZ")
        mmod.connectAttr(self.ankleCtrl.name+".rotateY", connectionGrp.name+".rotateY")
        mmod.connectAttr(self.ankleCtrl.name+".rotateZ", connectionGrp.name+".rotateX")
        # CLEAN-UP
        mc.parent(self.fingerGrp, connectionGrp)
        
        mmod.connectAttr(side+"_inverseFKIKBlend*_ADD.output", self.m_foot.footFKJnt[1].name+".visibility")
        parentConstraint = mc.parentConstraint(self.m_foot.footFKJnt[1].name, self.fingerGrp, mo=True)[0]
        weight = mc.parentConstraint(parentConstraint, q=True, wal=True)[0]
        mmod.connectAttr(side+"_inverseFKIKBlend*_ADD.output", parentConstraint+"."+weight)

        # mc.hide(self.m_foot.footFKJnt[1])
        # "L_inverseFKIKBlend049_ADD"
      
    

    def addFootRollAttr(self, side, ctrl, rollAttr=None, twistAttr=None, tarsalLockAttr=None, straightenAttr=None, toeRotationAttr=None, tarsalRotationAttr=None):
        
        # LEG TWIST
        if (twistAttr!=None):
            
            ctrl.addAttr( longName='legTwist', attrType='double' )     
            mmod.connectAttr(ctrl.name+".legTwist", twistAttr)

        # ROLL ATTR
        if (rollAttr!=None):
            ctrl.addAttr( longName='footRoll', attrType='double' )
            mmod.connectAttr(ctrl.name+".footRoll", rollAttr)

    
        # TOE ROTATION
        if (toeRotationAttr!=None):
            attrName = "toeRotation"
            ctrl.addAttr( longName='toeRotation', attrType='double' )
            addNode = mNode.addDoubleLinear(side=side, name=attrName+"AddToRestVal")
            mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
            mc.setAttr(addNode.getInput2(), mc.getAttr(toeRotationAttr))
            mmod.connectAttr(addNode.getOutput(), toeRotationAttr)

        if (tarsalRotationAttr!=None):
            attrName = "tarsalRotation"
            ctrl.addAttr( longName=attrName, attrType='double' )
            addNode = mNode.addDoubleLinear(side=side, name=attrName+"AddToRestVal")
            mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
            mc.setAttr(addNode.getInput2(), mc.getAttr(tarsalRotationAttr))
            mmod.connectAttr(addNode.getOutput(), tarsalRotationAttr)
            # TARSAL LOCK
        if (tarsalLockAttr!=None):
            attrName = "tarsalLock"
            ctrl.addAttr( longName=attrName, attrType='double' )
            addNode = mNode.addDoubleLinear(side=side, name=attrName+"AddToRestVal")
            mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
            mc.setAttr(addNode.getInput2(), mc.getAttr(tarsalLockAttr))
            mmod.connectAttr(addNode.getOutput(), tarsalLockAttr)
 
            
        # STRAIGHTEN
        if (straightenAttr!=None):
            attrName = "straighten"
            ctrl.addAttr( longName=attrName, attrType='double' )
            addNode = mNode.addDoubleLinear(side=side, name=attrName+"AddToRestVal")
            mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
            mc.setAttr(addNode.getInput2(), mc.getAttr(straightenAttr))
            mmod.connectAttr(addNode.getOutput(), straightenAttr)
        


    def addToePosesAttr(self, ctrl):
        ctrl.addAttr( longName='toePoses', attrType='double' )        
        ctrl.addAttr( longName='curl', attrType='double' )
        ctrl.addAttr( longName='spread', attrType='double' )
        ctrl.addAttr( longName='relax', attrType='double' )
        ctrl.addAttr( longName='clenched', attrType='double' )
        ctrl.addAttr( longName='fist', attrType='double' )

    def __init__(self, rigName, projectEnv):
        super(spinosaurus, self).__init__(rigName, projectEnv)

        # GLOBALS
        legMod.resetLegMod()
        armMod.resetArmMod()
        scapulaMod.resetScapulaMod()
        tailMod.resetTailMod()

        ########################################################################################################################################################################################################################                              
        #        BODY 
        ########################################################################################################################################################################################################################

        # Creating the spine
        self.m_spine = spineMod.spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self, revolveVector=[0, 0, 1])
        # Creating the neck
        self.m_neck = neckMod.neck(neckJnt="C_neck00_JNT", root=self.m_spine.chestCtl, parent=self, hook=self.m_spine.cog, revolveVector=[0, 0, 1])

        # Creating the tail
        self.m_tail = tailMod.tail(tailJnt="C_tail00_JNT", numbControlPoints=4, parent=self, root=self.m_spine.pelvisCtl)
        # Creating the arms, scapula, legs, foot
        side =["L", "R"]
        for s in side:

            self.m_arm =armMod.arm(side=s, armJnt=s+"_armShoulder00_JNT", parent=self, root=self.m_spine.chestCtl)
            self.m_scapula =scapulaMod.scapula(side=s, scapulaJnt=s+"_scapula00_JNT", parent = self, root=self.m_spine.chestCtl, armJnt=self.m_arm)
            self.m_leg = legMod.leg(legJnt=s+"_legHip00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            self.m_foot = foot(footJnt=s+"_footAnkle00_JNT", side=s, root=self.m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)

            
            # HAND
            self.m_hand =handMod.hand(handJnt=s+"_hand00_JNT", side=s, root=self.m_arm.effectorCtrl)

            # SPRING SOLVER
            self.springSolverLeg(side=s)
            # TOES
            m_thumbToe = handMod.finger(s+"_footThumb00_JNT", fingerName="thumbToe", side=s)#, parent=s+"_footFK_Ankle00_JNT")
            mc.parent(m_thumbToe.fingerGRP, s+"_footFK_Ankle00_JNT" )
            self.fingerGrp = mmod.transform(side=s, name="toes", type="GRP")
            m_indexToe = handMod.finger(s+"_footIndex00_JNT", fingerName="indexToe", side=s, parent=self.fingerGrp)
            m_middleToe = handMod.finger(s+"_footMiddle00_JNT", fingerName="middleToe", side=s, parent=self.fingerGrp)
            m_pinkyToe = handMod.finger(s+"_footPinky00_JNT", fingerName="pinkyToe", side=s, parent=self.fingerGrp)
            mc.parent(self.fingerGrp, s+"_footFK_Tarsals01_JNT")

            # CONNECT ANKLE TO TARSAL FK
            self.connectingAnkleTarsal(side=s)
            # ADD ATTRIBUTES TO CONTROLLER
            self.addFootRollAttr(s, self.ankleCtrl, rollAttr=s+"_legIKAnkle*_CTL.footRoll", twistAttr=s+"_legIKIKHandle00_IKH.twist", 
                                tarsalLockAttr=s+"_footRoll_animParameters*_GRP.tarsalLock", straightenAttr=s+"_footRoll_animParameters*_GRP.straighten",
                                tarsalRotationAttr=s+"_footRoll_configParameters*_GRP.tarsalRest", 
                                toeRotationAttr=s+"_footRoll_configParameters*_GRP.toeRest")
            # self.addToePosesAttr(self.ankleCtrl)


        ########################################################################################################################################################################################################################                              
        #        FACE 
        ########################################################################################################################################################################################################################
        # CREATING THE JAW
        self.m_jaw = jawMod.jaw(jawJnt="C_jaw00_JNT", root=self.m_neck.headCtrl)
   





       
        # TEMPORARY
        mc.hide("C_geometry01_GRP", "L_foot00_JNT", "R_foot00_JNT")



rig=spinosaurus("Spinosaurus", projectEnv)
