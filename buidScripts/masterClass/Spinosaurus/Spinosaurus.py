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


# Body Modules
import spineModule as spineMod
import neckModule as neckMod
import armModule as armMod
import scapulaModule as scapulaMod
import legModule as legMod
import footModule as footMod
import tailModule as tailMod
import handModule as handMod
# GLOBALS
hostName = socket.gethostname()

if (hostName == "DESKTOP-4NJ3EJ0"):
    projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-CM0E2QL"):
    projectEnv = "C:/Users/Kari Noriy/Desktop/Ana/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-PQV0HOV"):
    projectEnv = "C:/Users/AnaMaria/Documents/asRigging/projects/masterClass/"

# def ctrlAttribute(side, ctrl, attrName, attr, attrType):
#     attr = ctrl.addAttr(longName=attrName, attrType=attrType)
#     # Adding attr to original rest value
#     addNode = mNode.addDoubleLinear(side=side, name=attrName+"AddToRestVal")
#     mmod.connectAttr(ctrl.name+"."+attrName, addNode.getInput1())
#     mc.setAttr(addNode.getInput2(), mc.getAttr(attr))
#     mmod.connectAttr(addNode.getOutput(), attr)


class spine(object):
    def __init__(self, side="C", name="spine", revolveVector = [1, 0, 0], spineJnt=None, root=None, parent=None):
        '''
        SPINE MODULE

        1. CREATE JNT HIERARCHY
                > PELVIS
                > CHEST
                > SPINE RIBBON
    
        '''
        
        # GLOBALS
        self.side = side
        self.name = name
        self.root = root
        self.parent = parent
        self.guides = fn.descendentsList(root=spineJnt)
        self.spineJnt = []
        self.revolveVector = revolveVector
        self.forward = [0, -1, 0]
        self.up = [-1, 0, 0]
        mmod.resetCount() 
        # 1. CREATE JNT HIERARCHY
        # 1.0. PELVIS
        self.pelvisCtl = rigFn.constructCTL(self.guides[0], name = "pelvis", parent = self.root)
        # 1.2. COG CTRL
        self.cog = rigFn.constructCTL(self.guides[0], name = "COG", parent = self.root)
        fn.rotateShapePoints(self.cog.name, rotationVector=[0, 0, 90], pivot=mc.xform(self.guides[-1], q=True, ws=True, t=True))
        # 1.3. Spine FK
        self.fkCtl1 = rigFn.constructCTL(self.guides[len(self.guides)/2-2], name = self.name+"FKCtl", parent = self.cog)
        self.fkCtl2 = rigFn.constructCTL(self.guides[len(self.guides)/2+2], name = self.name+"FKCtl", parent = self.fkCtl1)
        # 1.4. CHEST
        self.chestCtl = rigFn.constructCTL(self.guides[-1], name="chest", parent = self.fkCtl2)

        # 2.0. SPINE RIBBON
        # Creating the Global Group
        self.spineGlobalGrp =  mmod.transform(side=self.side, name=self.name+"Global", type="GRP", parent=self.parent.rigGrp)
        # Create Surface Loft Guides
        self.createLoftSurface(self.guides[1:-1])
        # Attaching Joints
        self.attachJoinnts(parent=self.spineGlobalGrp)

        # 3.0 TWIST INTERPOLATOR
        self.twistDeformation()
        # DELETING GUIDES
        mc.delete(self.guides)

    def twistDeformation(self):
        '''
        For Creating the twist deformation we need to duplicate the surface twice and apply all the transformations in local space and then apply
        them to the deformation surface through because otherwise we encounter double transformations 

        '''
        # Duplicating the surface

        matloftSurface = mc.duplicate(self.surface, name="C_spineSurfaceDeformation01_NRB", rc=True)[0]
        mc.rename( fn.getChildren(matloftSurface)[0], "C_spineSurfaceDeformationShape01_SHP" )
        twistSurface = mc.duplicate(self.surface, name="C_spineTwistDeformation01_NRB" , rc=True)[0]
        mc.rename( fn.getChildren(twistSurface)[0], "C_spineTwistDeformationShape01_NRB")

        # Reconnecting matloft
        mmod.connectAttr(self.matloftNode.getOutputSurface(), fn.getChildren(matloftSurface)[0]+".create")
        mc.disconnectAttr(self.matloftNode.getOutputSurface(), self.surface+".create")

        # Applying Twist Deformation
        #   , lowBound=-1, highBound=1, startAngle=0, endAngle=0
        twistHandle = mc.nonLinear(twistSurface, type="twist")
        mc.xform(twistHandle[1], ro=[90, 0, 0])
        mc.parent(twistHandle, self.surfaceGuidesGrp)
        twistHandle[0] = mc.rename(twistHandle[0], "C_spineTwistNode00_TWS")
        twistHandle[1] = mc.rename(twistHandle[1], "C_spineTwistHandle00_HND")

        # Applying the surfaces as blendShapes to the main surface
        self.bShpName = "C_spineDeformation_BSHP"
        bShp = mc.blendShape(matloftSurface,  self.surface, n=self.bShpName)
        mc.blendShape(bShp, edit=True, t=(fn.getParent(self.surface), 1, twistSurface, 1.0))
        # Making infuence 1
        mc.setAttr(self.bShpName+"."+matloftSurface, 1)
        mc.setAttr(self.bShpName+"."+twistSurface, 1)

        # Connecting the Twist Handke to ChestCTL and Pelvis Ctl
        multNode = mNode.multDoubleLinear(side=self.side, name=self.name+"ReverseRot")
        mmod.connectAttr(self.pelvisCtl.name+".rotateX", multNode.getInput1())
        mc.setAttr(multNode.getInput2(), -1)
        mmod.connectAttr(multNode.getOutput(), twistHandle[1]+".startAngle")
        
        multNode = mNode.multDoubleLinear(side=self.side, name=self.name+"ReverseRot")
        mmod.connectAttr(self.chestCtl.name+".rotateX", multNode.getInput1())
        mc.setAttr(multNode.getInput2(), -1)
        mmod.connectAttr(multNode.getOutput(), twistHandle[1]+".endAngle")

        # HIDING TWIST HANDLE
        mc.hide(twistHandle)

    def createRivet(self, parameterU, parent=None):
        rivet = asNode.asRivet(side=self.side, name=self.name)
        group = mmod.transform(side=self.side, name=self.name, type="GRP", parent=parent)
        spineParent = mmod.transform(side=self.side, name="bind"+self.name.capitalize(), type="GRP", parent=self.pelvisCtl)
        fn.align(group, spineParent)
        # self.spineJnt.append(mmod.joint(side=self.side, name="bind"+self.name, parent= self.pelvisCtl))

        # self.spineJnt.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent=self.spineJnt[-1] if len(self.spineJnt)>0 else self.pelvisCtl))
        self.spineJnt.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent= spineParent))

        rivet.percentage = 1
        rivet.parameterU = parameterU

        mmod.connectAttr(self.surface+".worldSpace", rivet.getInputSurface())
        mmod.connectPlugs(rivet.outRotation, group.rotate)
        mmod.connectPlugs(rivet.outTranslation, group.translate)
        mc.setAttr(rivet.name+".forward", self.forward[0], self.forward[1], self.forward[2], type="double3")
        mc.setAttr(rivet.name+".up", self.up[0], self.up[1], self.up[2], type="double3")
        # GET GRP WORLD TRANSFORM
        matrixMult   = mNode.multMatrix(side=self.side, name=self.name)
        mmod.connectAttr(group.name+".worldMatrix", matrixMult.name+".matrixIn[0]")
        mmod.connectAttr(self.spineJnt[-1].name+".parentInverseMatrix", matrixMult.name+".matrixIn[1]")
        decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name)
        mmod.connectAttr(matrixMult.getMatrixSum(), decompMatrix.getInputMatrix())
        mmod.connectAttr(decompMatrix.getOutputTranslate(), self.spineJnt[-1].name+".translate" )
        mmod.connectAttr(group.name+".rotate" , self.spineJnt[-1].name+".rotate" )
        mmod.connectAttr(self.root.name+".scale", self.spineJnt[-1].name+".scale" )
        # mmod.connectAttr(group.name+".worldMatrix", decompMatrix.getInputMatrix)
        # mmod.connectAttr(group.name+".translate", self.spineJnt[-1].name+".translate" )
        # mc.parentConstraint( group, self.spineJnt[-1])
        # mmod.connectAttr(group.name+".translate", self.spineJnt[-1].name+".translate")
        # mmod.connectAttr(group.name+".rotate", self.spineJnt[-1].name+".rotate")
    def attachJoinnts(self, parent=None):
        group = mmod.transform(side=self.side, name=self.name+"BindJnt", type="GRP", parent=parent)

        for i in range (10):
            self.createRivet(i/10.0, parent=group)
            if (i>1 and i<7):
                self.createRivet(i/10.0+0.05, parent=group)



    def createLoftSurface(self, guides):
        self.surfaceGuides(guides)
        # Create surface from guides
        if (self.surfaceCtlPoints!=None):
            # Create matLoft node
            self.matloftNode = asNode.asMatloft(side=self.side, name=self.name+"Surface")
            # REVOLVE ORDER
            mc.setAttr(self.matloftNode.name+".revolveVector", self.revolveVector[0], self.revolveVector[1], self.revolveVector[2], type="double3")

            for k, obj in enumerate(self.surfaceCtlPoints):
                mc.connectAttr(obj.name+".worldMatrix", self.matloftNode.name+".inputMatrix["+str(k)+"]")

            self.surface = mc.createNode("nurbsSurface", name="C_spineSurfaceShape00_SHP")
            mc.rename(fn.getParent(self.surface), "C_spineSurface00_NRB" )
            mc.parent (self.surface, self.surfaceGuidesGrp)
            # Connecting surface
            mc.connectAttr(self.matloftNode.getOutputSurface(), self.surface+".create") 

            # Creating the Controls
            # MIDDLE
            middleCtl = rigFn.constructCTL(self.surfaceOfsPoints[2], name = self.name+"IKmiddle", parent = self.fkCtl1)
            mc.delete(mc.listRelatives(middleCtl.name, c=True)[1])
            fn.scaleShapePoints(middleCtl.name, mc.getAttr(guides[len(guides)/2]+".radius"))
            fn.rotateShapePoints(middleCtl.name, rotationVector=mc.xform(guides[len(guides)/2], q=True, ws=True, ro=True), pivot=mc.xform(guides[len(guides)/2], q=True, ws=True, t=True))
            mc.parent(self.surfaceOfsPoints[2], middleCtl)

            # # START
            mc.parent(self.surfaceOfsPoints[1], self.surfaceOfsPoints[0])
            mc.parentConstraint(self.pelvisCtl, self.surfaceOfsPoints[0], mo=True)
            # # END
            mc.parent(self.surfaceOfsPoints[3], self.surfaceOfsPoints[4])
            mc.parentConstraint(self.chestCtl, self.surfaceOfsPoints[4], mo=True)
            
    
    def influenceBlend(self, influence1=mmod.transform(), influence2=mmod.transform(), child=mmod.transform()):
        '''
        
        Blending the translation of the child between the two influences
        
        1. Adding up the transformations of the two influences
            matrixMult.input1 < influence1.worldMatrix
            matrixMult.input2 < influence2.worldMatrix

        2. Decompose transformations

        3. Averaging the transformation
            multiplyDivide.input1 < matrixMult.matrixSum
            multiplyDivide.input2 = [0.5, 0.5, 0.5]

        4. Connect output to child
            multiplyDivide.output > child.translate
        
        '''

        # 1. DecomMatrix
        decompMatrix1 = mNode.decomposeMatrix(side=self.side, name=self.name+"influence1")
        decompMatrix2 = mNode.decomposeMatrix(side=self.side, name=self.name+"influence2")
        mmod.connectAttr(influence1.name+".worldMatrix", decompMatrix1.getInputMatrix())
        mmod.connectAttr(influence2.name+".worldMatrix", decompMatrix2.getInputMatrix())
        # 2. Average Sum
        average = mNode.plusMinusAverage(side=self.side, name=self.name+"average")
        mmod.connectAttr(decompMatrix1.getOutputTranslate(), average.name+".input3D[0]")
        mmod.connectAttr(decompMatrix2.getOutputTranslate(), average.name+".input3D[1]")
        average.operation = 3
        # Connect Child
        mmod.connectAttr(average.getOutput3D(), child.name+".translate")
        
    def gradientInfluence(self, parent=None, child=None):
        '''
        Function that connects the movement of the child to the movement of the parent
        by an influence coefficient set to 0.5 by default


        1. Getting the world transformations of the parent
            Parent.worldMatrix => decompose Matrix

        2. Getting the difference between current transform and original transform
            plusMinAverage.input0 < decomMatrix.outputTransalate
            plusMinAverage.input1 = decompMatrix.outputTranslate
        
        3. Multiplying the result by the influence coefficient of the child
            multiplyDivide.input0 < plusMinAverage.output
            multiplyDivide.input1 < child.influence

        4. Adding the result to the original transformations of the child
            plusMinAverage.input0 < multiplyDivide.output
            plusMinAverage.input1 = child.translate
        
        5. Final connection
        '''
        if (parent!=None and child!=None):
            # Create influence attr for child
            influence = child.addAttr(longName="influence", softMinValue=-2, softMaxValue=2, defaultValue=0.5)
            # 1. GETTING PARENT WORLD TRANSFORMS
            parentWM = mNode.decomposeMatrix(side=self.side, name=parent.name)
            mmod.connectAttr(parent.getWorldMatrix(), parentWM.getInputMatrix())
            
            # 2. DIFFERENCE BETWEEN CURRENT TRANSLATION AND ORIGINAL
            difference = mNode.plusMinusAverage(side=self.side, name=parent.name+"TrasfDiff")
            mmod.connectAttr(parentWM.getOutputTranslate(), difference.name+".input3D[0]")
            outTrans = mc.getAttr(parentWM.getOutputTranslate())[0]
            mc.setAttr(difference.name+".input3D[1]", outTrans[0], outTrans[1], outTrans[2], type="double3")
            difference.operation = 2

            # 3. MULT BY INFLUENCE
            multNode = mNode.multiplyDivide(side=self.side, name=parent.name+"Influence")
            mmod.connectAttr(difference.getOutput3D(), multNode.getInput1())
            mmod.connectAttr(child.name+".influence", multNode.name+".input2X")
            mmod.connectAttr(child.name+".influence", multNode.name+".input2Y")
            mmod.connectAttr(child.name+".influence", multNode.name+".input2Z")

            # 4. ADDING TRANSF TO CHILD TRANSF
            plusNode = mNode.plusMinusAverage(side=self.side, name=parent.name+"Transf")
            mmod.connectAttr(multNode.getOutput(), plusNode.name+".input3D[0]")
            childTransf =mc.getAttr(child.name+".translate")[0]
            mc.setAttr(plusNode.name+".input3D[1]", childTransf[0], childTransf[1], childTransf[2], type="double3")
            
            # 5. CONNECTING RESULT TO CHILD
            mmod.connectAttr(plusNode.getOutput3D(), child.name+".translate")

    def createGuideFromObj(self, obj, parent=None):        
        ofs = mmod.transform(side=self.side, name=self.name+"offsetPoint", type="OFS", parent=parent)
        fn.align(obj, ofs)
        ctlPoint = mmod.transform(side=self.side, name=self.name+"ControlPoint", type="GRP", parent=ofs)
        self.surfaceOfsPoints.append(ofs)
        self.surfaceCtlPoints.append(ctlPoint)

    def surfaceGuides(self, guides):
        grp = mmod.transform(side=self.side, name=self.name+"SurfaceGuides", parent=self.spineGlobalGrp.name)
        self.surfaceGuidesGrp = grp
        self.surfaceOfsPoints = []
        self.surfaceCtlPoints = []
        mmod.resetTRNCount()

        # Getting guides position
        self.createGuideFromObj(guides[0], parent=grp)
        self.createGuideFromObj(guides[1], parent=grp)

        # Middle Guide
        gLen = len(guides)
        if (gLen%2!=0):
            self.createGuideFromObj(guides[gLen/2], parent=grp)
        # Even number of guides
        else:
            midGuide = mmod.transform()
            mc.select(guides[gLen/2-1], guides[gLen/2], midGuide)
            fn.alignTool()
            self.createGuideFromObj(midGuide, parent=grp)
            mc.delete(midGuide)
        self.createGuideFromObj(guides[gLen-2], parent=grp)
        self.createGuideFromObj(guides[gLen-1], parent=grp)  


class jaw(object):
    def __init__(self, side="C", name="jaw", jawJnt=None, root=None, parent=None, hook=None):
        '''
        JAW MODULE
    
        '''
        
        # GLOBALS
        self.side = side
        self.name = name
        self.root = root
        self.parent = parent
        self.hook = hook
        self.guides = fn.descendentsList(root=jawJnt)
        self.neckJnt = []
        mmod.resetCount() 
        # 1. CREATE JNT HIERARCHY
        # 1.0. JAW 
        self.jawJnt = rigFn.constructJNT(self.guides[0], side=self.side, name="bind"+self.name.capitalize(), parent = self.root)
        self.jawCtrl = rigFn.constructCTL(self.guides[-1], name = "bind"+self.name.capitalize(), parent = self.root)
        print fn.getChildren(self.jawCtrl.name)[1]
        mc.parent (fn.getChildren(self.jawCtrl.name)[1], self. jawJnt.name)

        # 2. CONNECT CTRL TO JAW ROTATION
        # CREATE REST POSE GUIDES
        jawRest = mmod.transform(side=self.side, name="jawRestGuide", type="GRP", parent = self.guides[0])
        mc.parent (jawRest.name, fn.getChildren(self.root)[1])
        jawCtrlRest = mmod.transform(side=self.side, name="jawCtrlRestGuide", type="GRP", parent = self.guides[1])
        mc.parent (jawCtrlRest.name, fn.getChildren(self.root)[1])
        # GET REST POSE VECTOR
        # ctrlPoz = mc.xform(self.jawCtrl.name, q=True, t=True, ws=True) 
        # jntPoz = mc.xform(self.jawJnt.name, q=True, t=True, ws=True)
        # restPoseVector = [ctrlPoz[0]-jntPoz[0], ctrlPoz[1]-jntPoz[1], ctrlPoz[2]-jntPoz[2]]
        # print restPoseVector


        worldMatrixCtrl = mNode.decomposeMatrix(side=self.side, name=self.name+"RestCtlWM")
        mmod.connectAttr(jawCtrlRest.name+".worldMatrix", worldMatrixCtrl.getInputMatrix())        
        worldMatrixJnt = mNode.decomposeMatrix(side=self.side, name=self.name+"RestJntWM")
        mmod.connectAttr(jawRest.name+".worldMatrix", worldMatrixJnt.getInputMatrix())
        restVect = mNode.plusMinusAverage(side=self.side, name=self.name+"RestVect")
        mc.setAttr(restVect.getOperation(), 2)
        mmod.connectAttr(worldMatrixCtrl.getOutputTranslate(), restVect.name+".input3D[0]")
        mmod.connectAttr(worldMatrixJnt.getOutputTranslate(), restVect.name+".input3D[1]")

        # TRANSFORMATION VECTOR
        worldMatrixCtrl = mNode.decomposeMatrix(side=self.side, name=self.name+"CtlWM")
        mmod.connectAttr(self.jawCtrl.name+".worldMatrix", worldMatrixCtrl.getInputMatrix())        
        # worldMatrixJnt = mNode.decomposeMatrix(side=self.side, name=self.name+"JntWM")
        mmod.connectAttr(self.jawJnt.name+".worldMatrix", worldMatrixJnt.getInputMatrix())
        transformVect = mNode.plusMinusAverage(side=self.side, name=self.name+"TransformationVect")
        mc.setAttr(transformVect.getOperation(), 2)
        mmod.connectAttr(worldMatrixCtrl.getOutputTranslate(), transformVect.name+".input3D[0]")
        mmod.connectAttr(worldMatrixJnt.getOutputTranslate(), transformVect.name+".input3D[1]")

        # CALCULATING ANGLE BETWEEN
        angleBetween = mNode.angleBetween(side=self.side, name="jawRotationAngle")
        mmod.connectAttr(restVect.getOutput3D(), angleBetween.getVector1())
        mmod.connectAttr(transformVect.getOutput3D(), angleBetween.getVector2())
        # CONNECTING ROTATION
        inverseX = mNode.animBlendNodeAdditiveDA(side=self.side, name=self.name+"InverseRotX")
        mmod.connectAttr(angleBetween.name+".eulerZ", self.jawJnt.name+".rotateX")
        mmod.connectAttr(angleBetween.name+".eulerY", self.jawJnt.name+".rotateY")
        mmod.connectAttr(angleBetween.name+".eulerX", inverseX.getInputA())
        mc.setAttr(inverseX.getWeightA(), -1)
        mmod.connectAttr(inverseX.getOutput() , self.jawJnt.name+".rotateZ")

        # DELETING GUIDE
        mc.delete(self.guides[0])


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


        # # 5. CONNECT FOOTROLL TO FK FOOT (WITH CONSTRAINTS)
        # # ROLL TOES > FK TARSAL
        # toeOrientConstraint = mc.orientConstraint(footRolljnt[1].name, fn.getParent(self.footFKJnt[1].name), mo=True)[0]
        # tarsalOrientConstraint = mc.orientConstraint(footRolljnt[2].name, fn.getParent(fn.getParent(self.footFKJnt[0].name)), mo=True)[0]
        # # Set influence to be active just in IK mode
        # weight = mc.orientConstraint(toeOrientConstraint, q=True, wal=True)[0]
        # mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", toeOrientConstraint+"."+weight)
        # weight = mc.orientConstraint(tarsalOrientConstraint, q=True, wal=True)[0]
        # mmod.connectAttr(self.legRoot.settingCtl.name+".fkIkBlend", tarsalOrientConstraint+"."+weight)

        # self.legRoot.blendAttr

        # 5. CONNECT FOOTROLL TO FK FOOT (WITH NODES)
        # 5.0. Get Heel Toe Vector (bind pose value)
        heelToeVect=[]
        pHeel = mc.xform(footRolljnt[0].name, q=True, t=True, ws=True)
        pToes = mc.xform(footRolljnt[1].name, q=True, t=True, ws=True)
        for i in range (3):
            heelToeVect.append(pToes[i]-pHeel[i])

        # 5.1. Get Ankle Tarsal Vector 
        plusMinAnkleTarsalVect = mNode.plusMinusAverage(side=self.side, name="footRoll"+"ankleTarsalVect")
        decompMtxFootRollTarsal = mNode.decomposeMatrix(side=self.side, name="footRoll"+"footRollTarsal")
        mmod.connectAttr(footRolljnt[2].name+".worldMatrix", decompMtxFootRollTarsal.name+".inputMatrix") 
        mc.setAttr(plusMinAnkleTarsalVect.getOperation(), 2)
        mmod.connectAttr(decompMtxFootRollTarsal.getOutputTranslate(), plusMinAnkleTarsalVect.name+".input3D[0]")
        mmod.connectAttr(decompMtxFootRollAnkle.getOutputTranslate(), plusMinAnkleTarsalVect.name+".input3D[1]")

        # 5.2. Angle Between vectors
        angleBetweenVect = mNode.angleBetween(side=self.side, name="footRoll"+"angleBetween")
        mc.setAttr(angleBetweenVect.getVector1(), heelToeVect[0], heelToeVect[1], heelToeVect[2], type="double3")
        mmod.connectAttr(plusMinAnkleTarsalVect.getOutput3D(), angleBetweenVect.getVector2())
        
        # 5.3. Hook Foot GRP
        # Getting World Transformations
        decompMtxAnkeCtl = mNode.decomposeMatrix(side=self.side, name="legAnkleCtrlWM")
        mmod.connectAttr(self.legRoot.effectorCtrl.name+".worldMatrix", decompMtxAnkeCtl.getInputMatrix())
        animBlendRotX = mNode.animBlendNodeAdditiveDA(side=self.side, name="footRoll"+"ankleAddingRotationX")
        animBlendRotY = mNode.animBlendNodeAdditiveDA(side=self.side, name="footRoll"+"ankleAddingRotationY")
        mmod.connectAttr(decompMtxAnkeCtl.name+".outputRotateX", animBlendRotX.getInputA())
        mmod.connectAttr(angleBetweenVect.name+".eulerX", animBlendRotX.getInputB())

        mmod.connectAttr(decompMtxAnkeCtl.name+".outputRotateY", animBlendRotY.getInputA())
        mmod.connectAttr(angleBetweenVect.name+".eulerY", animBlendRotY.getInputB())
        
        mmod.connectAttr(animBlendRotX.getOutput(), self.footFKGRP+".rotateX")
        mmod.connectAttr(animBlendRotY.getOutput(), self.footFKGRP+".rotateY")
        #mmod.connectAttr(decompMtxAnkeCtl.name+".outputRotateY", self.footFKGRP+".rotateY")
        mmod.connectAttr(decompMtxAnkeCtl.name+".outputRotateZ", self.footFKGRP+".rotateZ")
        # Reorient Ankle OFS
        mc.delete(mc.orientConstraint(footJNTList[3], fn.getParent(self.footFKJnt[0]), mo=False))
        
        # 5.4. Hook Toes
        hook = fn.getParent(self.footFKJnt[1].name)
        animBlend = mNode.animBlendNodeAdditiveDA(side=self.side, name="footRoll"+"tarsalRotationX")
        mmod.connectPlugs(footRolljnt[2].rotateZ, animBlend.inputA)
        # mc.setAttr(animBlend.getWeightA(), -1)
        mc.setAttr(animBlend.getInputB(), mc.getAttr(hook+".rotateZ"))
        mmod.connectAttr(animBlend.getOutput(), hook+".rotateZ")

        # 6. Connecting FootRoll to leg Ctrl
        mmod.connectPlugs(self.legRoot.footRollAttr, self.footRoll)

        # CONSTRAINT FOOT ROLL JNT TO ROOT
        # constr = mc.parentConstraint(fn.getParent(self.hook.name), fn.getParent(footRolljnt[0].name), mo=True)
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



class finger(object):
    globalCtrl=None
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
            mc.aimConstraint(fingerBaseJnt[i+1], fingerBaseJnt[i], aim=[1, 0, 0], u=[0, 1, 0])

            
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
            mc.connectAttr(minusNode+".output1D", fn.getChildren(fingerBaseJnt[i])[0]+".translateX")

            # POSITIONING END JNT
            if (jnt==guidJntList[-2]):
                translateX = mc.getAttr(guidJntList[-1]+".translateX")
                mc.setAttr(fn.getChildren(fingerBaseJnt[-1])[0]+".translateX", translateX)


        self.fingerJntChain = fingerBaseJnt

        # DELETING GUIDES
        #mc.delete(jntHierarchy)

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
        self.m_spine = spine(spineJnt="C_spine00_JNT", root=self.rootJnt, parent=self)
        # Creating the neck
        # self.m_neck = neckMod.neck(neckJnt="C_neck00_JNT", root=self.m_spine.chestCtl, parent=self, hook=self.m_spine.cog)

        # Creating the tail
        self.m_tail = tailMod.tail(tailJnt="C_tail00_JNT", numbControlPoints=4, parent=self, root=self.m_spine.pelvisCtl)
        # Creating the arms, scapula, legs, foot
        side =["L", "R"]
        for s in side:

            self.m_arm =armMod.arm(side=s, armJnt=s+"_armShoulder00_JNT", parent=self, root=self.m_spine.chestCtl)
            self.m_scapula =scapulaMod.scapula(side=s, scapulaJnt=s+"_scapula00_JNT", parent = self, root=self.m_spine.chestCtl, armJnt=self.m_arm)
            self.m_leg =legMod.leg(legJnt=s+"_legHip00_JNT", side=s, parent=self, root=self.m_spine.pelvisCtl)
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
        # self.m_jaw = jaw(jawJnt="C_jaw00_JNT", root=self.m_neck.headCtrl)
   





       
        # TEMPORARY
        mc.hide("C_geometry01_GRP", "L_foot00_JNT", "R_foot00_JNT")



rig=spinosaurus("Spinosaurus", projectEnv)
