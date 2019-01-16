
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
import blendFKIK as blendFKIK


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


def createGuides(side, numberOfGuides, spacing=1):
    mmod.locator.elemIndex=0
    guideList=[]
    for i in range (numberOfGuides):
        guideList.append(mmod.locator(side=side, name= "locGuide"))
        mc.xform(guideList[i], t=[i*spacing, 0, 0])
    return guideList

def loftSurfaceFromGuides(side="C",name="matloft",guides=None):    
    if (guides!=None):
            
        # Create matLoft node
        matloft = asNode.asMatloft(side=side, name=name)

        for k, obj in enumerate(guides):
            mc.connectAttr(obj.name+".worldMatrix", matloft.name+".inputMatrix["+str(k)+"]")

        
        
        return matloft


class ribbon(object):
    def __init__(self, side="C", name="ribbon", guides=None, parent=None):
        # GLOBALS
        asNode.asRivet.elemIndex=0
        asNode.asMatloft.elemIndex=0
        mmod.resetCount()

        self.side=side
        self.name = name
        self.parent = parent
        if (guides!=None):
            matloftNode = loftSurfaceFromGuides(side=side, name=name, guides=guides)
        
        # For VISUALIZATION        
        surface = mc.createNode("nurbsSurface")
        # Connecting surface
        mc.connectAttr(matloftNode.getOutputSurface(), surface+".create") 
        mc.rebuildSurface(surface, su=len(guides)*2, sv=1, kr=2)

        # RIVETS
        numbGuides = len(guides)
        parentGroup = mmod.transform(side=self.side, name=self.name+"Joints", parent = self.parent)
        for i in range (numbGuides-1):
           
            rivet = asNode.asRivet(side=self.side, name=self.name)
            group = mmod.transform(side=self.side, name=self.name, parent=parentGroup)
            rivet.percentage = 1
            coef = 1.0/(numbGuides*2.0)
            rivet.parameterU = coef*(i*2+1)
            mmod.connectAttr(surface+".worldSpace", rivet.getInputSurface())
            mmod.connectPlugs(rivet.outRotation, group.rotate)
            mmod.connectPlugs(rivet.outTranslation, group.translate)
            mc.setAttr(rivet.name+".forward", 0, 1, 0, type="double3")
            mc.setAttr(rivet.name+".up", 1, 0, 0, type="double3")
            # Parent Inverse Matrix
            mmod.connectAttr(parentGroup.name+".worldInverseMatrix", rivet.name+".parentInverseMatrix")
            # Creating the joints
            joint = mmod.joint(name=self.name, side=self.side, parent=group)



def testProject():
    guides = createGuides("C", 5, spacing=3)
    asRibbon = ribbon(guides=guides)



class ribbonLimbs(object):
    def generateGuides(self):
        '''
        1. GET SEGMENT DIRECTION VECTOR
        2. NORMALIZE VECTOR
        3. CREATE GUIDES

        '''
        # 0. GLOBAL GROUP
        self.guideGrp = mmod.transform(side=self.side, name=self.name+"Guides", parent = self.parent, type="GRP")
        self.controlGrp = mmod.transform(side=self.side, name=self.name+"ControlGuides", parent = self.guideGrp, type="GRP")

        # 1. GET SEGMENT DIRECTION VECTOR
        # 1.0. Get Start and End Positions
        guide0 = mc.xform(self.startJnt, ws=True, q=True, t=True)
        guide4 = mc.xform(self.endJnt, ws=True, q=True, t=True)
        # 1.1. Get Vector
        directionVector = []
        for component0, component4 in zip(guide0, guide4):
            directionVector.append(component4-component0)
        # 2. NORMALIZE VECTOR
        # 2.0. Get Vector Length
        vectorLength = fn.deistBetween(guide0, guide4)
        # 2.1. Normalize directionVector
        for i in range (len(directionVector)):
            directionVector[i] = directionVector[i]/vectorLength
        # 3. CREATE GUIDES
        for i in range (self.numbGuides):
            self.guides.append(mmod.transform(side=self.side, name=self.name+"Guide", type="GRP", parent=self.controlGrp))
            transformation =[] 
            for p0, v0 in zip(guide0, directionVector):
                transformation.append(p0+v0*(i*vectorLength/(self.numbGuides-1)))
            mc.xform(self.guides[i], ws=True, t=transformation )

    def __init__(self, side="C", name="ribbbonLimb", numberOfGuides=5, endJnt=None, startJnt=None, parent=None, root=None):
        # self
        self.side = side
        self.name = name
        self.endJnt = endJnt
        self.startJnt = startJnt
        self.parent = parent
        self.root = root
        self.guides = []
        self.numbGuides = numberOfGuides
        # GLOBALS
        mmod.resetCount()
        # SET UP
        if (endJnt!=None, startJnt!=None):
            self.generateGuides()
            # CREATING THE RIBBONS
            ribbon(side=self.side, name=self.name, guides=self.guides, parent=self.root)




class leg(blendFKIK.blendFKIK):
    rigParent = None
    def __init__(self, side="C", legJnt=None, parent=None, root=None):
        if (parent!=None):
            if(leg.rigParent==None):
                leg.rigParent=mmod.transform(name="legGlobal", type="GRP", parent=parent.rigGrp)
        super(leg, self).__init__(side=side, jnt=legJnt, name="leg", segmentsList=["Hip", "Knee", "Ankle"], parent=leg.rigParent, root=root,  hook=parent.rootJnt)
        # FootRoll Attribute
        self.footRollAttr = self.effectorCtrl.addAttr(longName="footRoll", softMinValue=-1.7, defaultValue=0, softMaxValue=3.14, attrType="doubleAngle", keyable=True)
        # RIBBON LIMBS
        ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "femurRibbon", parent=leg.rigParent, root=root)
        # ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "tibiaRibbon")

class arm(blendFKIK.blendFKIK):
    '''
    side = Arm side (L, R, C)
    armJnt = guideJnt (first jnt in chain)
    parent = rig class 
    root = parent of bind Jnts (under what jnt does the user want the joints to be created)
    '''
    rigParent=None
    def __init__(self, side="C", armJnt = None, parent=None, root=None):
        if (parent!=None):
            if (arm.rigParent==None):
                arm.rigParent=mmod.transform(name="armGlobal", type="GRP", parent=parent.rigGrp)

        super(arm, self).__init__(side=side, jnt=armJnt, name="arm", segmentsList=["Shoulder", "Elbow", "Wrist"], parent=arm.rigParent, root=root, hook=parent.rootJnt)
        # RIBBON LIMBS
        # ribbonLimbs(side=self.side, endJnt=self.bindJntChain[1], startJnt=self.bindJntChain[0], name= "humerusRibbon")
        # ribbonLimbs(side=self.side, endJnt=self.bindJntChain[2], startJnt=self.bindJntChain[1], name= "radiusRibbon")
    


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
        self.m_tail = tailMod.tail(tailJnt="C_tail00_JNT", numbControlPoints=4, parent=self, root=self.m_spine.pelvisCtl)
        # Creating the arms, scapula, legs, foot
        side =["L", "R"]
        for s in side:

            self.m_arm =arm(side=s, armJnt=s+"_armShoulder00_JNT", parent=self, root=self.m_spine.chestCtl)
            self.m_scapula =scapulaMod.scapula(side=s, scapulaJnt=s+"_scapula00_JNT", parent = self, root=self.m_spine.chestCtl, armJnt=self.m_arm)
            self.m_leg = leg(legJnt=s+"_legHip00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
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
