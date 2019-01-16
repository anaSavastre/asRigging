
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


    
class tail (object): 
    rigParent=None
    def __init__(self, side="C", tailJnt = None, numbControlPoints=3, name="tail", parent = None, root=None):
        '''
        Tail Types of Controls:
            > Normal FK Controls
            > Global Curl Control
            > Segment Curl Control
        > Switch Between Controls Using a Visibility Switch 
        '''
        # self
        self.side = side
        self.jntGuide = tailJnt
        
        self.parent = parent
        self.root = root
        self.name = name
        self.numbControlPoints = numbControlPoints

        
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()

        if (parent!=None):
            if (tail.rigParent==None):
                tail.rigParent=mmod.transform(name="tailGlobal", type="GRP", parent=parent.rigGrp)


        if (tailJnt!=None):
            # 1. CREATING THE HIERARCHY
            # FK JNT CHAIN FROM GUIDES
            self.jntGuideList = fn.descendentsList(root=self.jntGuide)
            tailGrp = mmod.transform(side=self.side, name=self.name, type="GRP", parent=self.root)

            # Creating Sec CTL
            self.jntChain = rigFn.createFKChain(self.jntGuideList[1:], side=self.side, name="bind"+self.name.capitalize(), parent=tailGrp)

            # Creating mainControls: mainCtrl, CurCtrl
            offset = len(self.jntChain)/self.numbControlPoints
            mainCtrlParent = mmod.transform(side=self.side, name=self.name+"MainCtrl", type="GRP", parent=tail.rigParent)
            # Parenting main Ctrl to Pelvis
            mc.parentConstraint(self.root, mainCtrlParent.name) 
            # Scaling
            mmod.connectAttr(fn.getParent(self.parent.rootJnt)+".scale", mainCtrlParent.name+".scale")
            curlCtrlParent = mmod.transform(side=self.side, name=self.name+"CurlCtrl", type="GRP", parent=tail.rigParent) 
            mainCtrlList = []
            curlCtrlList = []
            # GLOBAL CURL CTRL
            globalCurlCtrl = rigFn.constructCTL(self.jntGuideList[1], side=self.side, name=self.name+"globalCurlCtrl", parent=curlCtrlParent)
            fn.scaleShapePoints(globalCurlCtrl.name, 1.5)
            for i in range (1, len(self.jntChain)-2, offset):
                # MAIN CTRL
                ctrl = rigFn.constructCTL(self.jntGuideList[i], side=self.side, name="control"+self.name, parent=mainCtrlParent)
                fn.scaleShapePoints(ctrl.name, 1.3)
                
                newGrp = mmod.transform(side=self.side, name="bind"+self.name.capitalize(), parent=fn.getParent(self.jntChain[i-1].name), type="GRP")
                mc.parent(self.jntChain[i-1].name, newGrp)

                # Connecting ctrl transfromations to newGrp
                mmod.connectPlugs(ctrl.translate, newGrp.translate)
                mmod.connectPlugs(ctrl.rotate, newGrp.rotate)
                mmod.connectPlugs(ctrl.scale, newGrp.scale)

                mainCtrlList.append(ctrl)
                mainCtrlParent = ctrl

                # CURL CTRL
                curlCtrl = rigFn.constructCTL(self.jntGuideList[i], side=self.side, name="curlCtrl"+self.name, parent=curlCtrlParent)
                # Making curlCtrl follow bindJnt
                # Get NewGrp World Matrix
                decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name+"BindWM")
                mmod.connectAttr(newGrp.getWorldMatrix(), decompMatrix.getInputMatrix())
                mmod.connectAttr(decompMatrix.getOutputTranslate(), fn.getParent(curlCtrl.name)+".translate")
                mmod.connectAttr(decompMatrix.getOutputRotate(), fn.getParent(curlCtrl.name)+".rotate")
                mmod.connectAttr(decompMatrix.name+".outputScale", fn.getParent(curlCtrl.name)+".scale")
                # Curl Effect
                # Creating add nodes
                if (i>=1):
                    if (i==offset+1):
                        addNode = mNode.plusMinusAverage(side=self.side, name=self.name+"CurlAddition")
                        mmod.connectAttr(globalCurlCtrl.name+".rotate", addNode.name+".input3D[0]")
                        mmod.connectAttr(curlCtrl.name+".rotate", addNode.name+".input3D[1]")
                        addObj = addNode

                    else:
                        addNode = mNode.plusMinusAverage(side=self.side, name=self.name+"CurlAddition")
                        mmod.connectAttr(globalCurlCtrl.name+".rotate", addNode.name+".input3D[0]")
                        mmod.connectAttr(curlCtrl.name+".rotate", addNode.name+".input3D[1]")
                        addObj = addNode
                # Connecting add nodes to jnt Rotation
                for j in range (offset+1):
                    mmod.connectAttr(addNode.getOutput3D(), fn.getParent(self.jntChain[i+j].name)+".rotate")

                    # if (i==1):
                    #     mmod.connectAttr(curlCtrl.name+".rotate", fn.getParent(self.jntChain[i+j].name)+".rotate")

                    # else:

                curlCtrlList.append(curlCtrl)

                fn.scaleShapePoints(curlCtrl.name, 1.3)
                mc.delete(fn.getChildren(curlCtrl)[1])

                

            # Creating Visibility ATTR
            visibility = globalCurlCtrl.addAttr(longName="secondaryCtl", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short")
            curlCtrlVisibility = globalCurlCtrl.addAttr(longName="curlCtrl", softMinValue=0, defaultValue=1, softMaxValue=1, attrType="short")
            # fkCtrlVisibility = mainCtrlList[0].addAttr(longName="curlCtrl", softMinValue=0, defaultValue=1, softMaxValue=1, attrType="short")
            for jnt in (self.jntChain):
                mmod.connectPlugs(visibility, jnt.visibility)
            # # Switchin visibility off from MainCtrls
            # subtractNode = mNode.plusMinusAverage(side=self.side, name=self.name+"ReverseVisibilitySwitch")
            # subtractNode.operation = 2
            # mc.setAttr(subtractNode.name+".input1D[0]", 1)
            # mmod.connectAttr(mainCtrlList[0].name+".secondaryCtl", subtractNode.name+".input1D[1]")
            # mmod.connectAttr(subtractNode.name+".output1D", mainCtrlList[1].name+".visibility")

            # Curl Control Visibility
            for ctrl in curlCtrlList:
                mmod.connectPlugs(curlCtrlVisibility, ctrl.visibility)
            
            # FK Control Visibility
            addition = mNode.addDoubleLinear(side = self.side, name=self.name+"curlSecondaryAdd")
            mmod.connectAttr(globalCurlCtrl.name+".secondaryCtl", addition.getInput1())
            mmod.connectAttr(globalCurlCtrl.name+".curlCtrl", addition.getInput2())
            condition = mNode.condition(side=self.side, name=self.name+"FKControlVisibility")
            condition.operation = 0
            mmod.connectPlugs(addition.output, condition.firstTerm)
            mc.setAttr(condition.getSecondTerm(), 0)
            mc.setAttr(condition.getColorIfFalse(), 0, 0, 0, type = "double3")
            mc.setAttr(condition.getColorIfTrue(), 1, 1, 1, type = "double3")
            mmod.connectAttr(condition.name+".outColorR", mainCtrlList[0].name+".visibility")
                
        # DELETING GUIDES
        mc.delete(tailJnt)





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
        globalEffectorAimGrp = mmod.transform(side =side, name="tarsalAimEffectorGlobalMove", parent=side+"_ankle*_GRP")
        
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
        self.m_tail = tail(tailJnt="C_tail00_JNT", numbControlPoints=4, parent=self, root=self.m_spine.pelvisCtl)
        # Creating the arms, scapula, legs, foot
        side =["L", "R"]
        for s in side:

            self.m_arm =armMod.arm(side=s, armJnt=s+"_armShoulder00_JNT", parent=self, root=self.m_spine.chestCtl)
            self.m_scapula =scapulaMod.scapula(side=s, scapulaJnt=s+"_scapula00_JNT", parent = self, root=self.m_spine.chestCtl, armJnt=self.m_arm)
            self.m_leg = legMod.leg(legJnt=s+"_legHip00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
            self.m_foot = footMod.foot(footJnt=s+"_footAnkle00_JNT", side=s, root=self.m_leg, parent=s+"_bindLeg00_GRP", hook=self.rootJnt)

            
            # HAND
            self.m_hand =handMod.hand(handJnt=s+"_hand00_JNT", side=s, root=self.m_arm, parent= s+"_bindArm00_GRP", hook = self.rootJnt)

            # SPRING SOLVER
            self.springSolverLeg(side=s)
            # TOES
            m_thumbToe = handMod.finger(s+"_footThumb00_JNT", fingerName="thumbToe", side=s, hook = self.rootJnt)#, parent=s+"_footFK_Ankle00_JNT")
            mc.parent(m_thumbToe.fingerGRP, s+"_footFK_Ankle00_JNT" )
            self.fingerGrp = mmod.transform(side=s, name="toes", type="GRP")
            m_indexToe = handMod.finger(s+"_footIndex00_JNT", fingerName="indexToe", side=s, parent=self.fingerGrp, hook = self.rootJnt)
            m_middleToe = handMod.finger(s+"_footMiddle00_JNT", fingerName="middleToe", side=s, parent=self.fingerGrp, hook = self.rootJnt)
            m_pinkyToe = handMod.finger(s+"_footPinky00_JNT", fingerName="pinkyToe", side=s, parent=self.fingerGrp, hook = self.rootJnt)
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
