import maya.cmds as mc
import functions as fn
import rigFn
import mayaModule as mmod
import mayaNode as mNode
import ribbon as ribbon



class lips(object):
    def __init__(self, side="C", name="lips", lipUpper=None, lipLower=None, lipCorners = None, jawJNT = None, root=None, parent=None, hook=None):

        '''
        lipUpper = group that contains all the joints separately

        lipLower = group that contains all the joints separately

        lip Corners = same  as above

        root = direct descendence
        parent = Extras (rigGRP)
        hook = rootJNT -> for global scaling

        ''' 
        # GLOBALS
        self.side = side
        self.name = name
        self.root = mmod.transform(name="lipsRoot", type="GRP", parent = root)
        self.parent = parent
        self.hook = hook
        self.jawJnt = jawJNT

        self.lipUpperGuide = fn.getChildren(lipUpper)
        self.lipLowerGuide = fn.getChildren(lipLower)
        self.lipCornersGuide = fn.getChildren(lipCorners)

        mmod.resetCount() 

        # 1. CREATE CORNER CONTROLS
        leftCorner  = rigFn.constructCTL(self.lipCornersGuide[0], side="L", name="lipsCorner", parent=self.root, ctrlShape=6)
        rightCorner = rigFn.constructCTL(self.lipCornersGuide[1], side="R", name="lipsCorner", parent=self.root, ctrlShape=6)
        
        # 2. CREATE RIBBONS
        # 2.0. Creating lips Global Group
        self.parent = mmod.transform(name=self.name+"Global", type="GRP", parent=self.parent)
        # 2.1. Creating Lips Controls
        # Upper
        self.upperControls = []
        for guide in self.lipUpperGuide:
            ctrl = rigFn.constructCTL(guide, name = "localUpperLip", parent = self.root, ctrlShape=6)
            mc.delete(fn.getChildren(ctrl)[-1])
            jnt= mmod.joint(side=self.side, name="localUpperLip", parent=ctrl)
            self.upperControls.append(jnt)
            # Sacling Child Joint Radius to 
            mc.setAttr(self.upperControls[-1].name+".radius", 0.1)

        # Lower
        self.lowerControls = []
        for guide in self.lipLowerGuide: 
            ctrl = rigFn.constructCTL(guide, name = "localLowerLip", parent = self.jawJnt, ctrlShape=6)
            mc.delete(fn.getChildren(ctrl)[-1])
            jnt= mmod.joint(side=self.side, name="localLowerLip", parent=ctrl)
            self.lowerControls.append(jnt)
            # Sacling Child Joint Radius to 
            mc.setAttr(self.upperControls[1].name+".radius", 0.1)


        # Upper Lip
        self.upperLipRibbon = ribbon.ribbon(name=self.name+"UpperRibbon", guides=self.upperControls, 
                            numberOfJoints=len(self.upperControls), revolveVector= [0, 0, 1], parent=self.parent, root=self.root)
        # LowerLip
        self.lowerLipRibbon = ribbon.ribbon(name=self.name+"LowerRibbon", guides=self.lowerControls, 
                            numberOfJoints=len(self.lowerControls), revolveVector= [0, 0, 1], parent=self.parent, root=self.jawJnt)

        # 3. CREATE LIP AUTO MOVEMENT
        self.lipAutoMovement ()

        # 4. CREATING CONTROLLER STRUCTURE

    def auxiliarySetUp (self, guide, worldUp, parent):
        # Creating Joint
        parentJnt= mmod.joint(side=self.side, name="global"+"LipGuide", parent=parent)
        # Align With Guide
        fn.align(guide, parentJnt)
        # Offset By Radius
        mc.xform (parent, ws=True, t=[0, 0, mc.getAttr(parentJnt.name+".radius")])
        # Create Children 
        childJnt= mmod.joint(side=self.side, name="global"+"LipGuide", parent=parentJnt)
        # AimConstraint
        mc.aimConstraint (guide, parentJnt, aim=[0, 0, 1], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=worldUp)

        # DistanceBetween
        distanceNode = mNode.distanceBetween(side=self.side, name="guideToLipDist")
        mmod.connectAttr(parentJnt.getWorldMatrix(), distanceNode.getInMatrix1())
        mmod.connectAttr(guide.getWorldMatrix(), distanceNode.getInMatrix2())
        mmod.connectAttr(distanceNode.getDistance(), childJnt.name+".translateZ")        

        return childJnt.name


    def lipCollisionSetUp (self, causeObj, effectObj, root, translationDirection=1, name="name"):
        # Create Necessary Nodes
        matrixMult = mNode.multMatrix(side=self.side, name=name+"SpaceMatrix")
        decompWorldMatrix = mNode.decomposeMatrix(side=self.side, name=name+"WM")
        deltaTranslation = mNode.plusMinusAverage(side=self.side, name=name+"DeltaTranslation")
        offset = mNode.plusMinusAverage(side=self.side, name=name+"Offset")
        clamp = mNode.clamp(side=self.side, name=name+"AutoMovClamp")
        if (translationDirection<0):
            reversedDirection = mNode.multDoubleLinear(side=self.side, name=name+"Reverse")
        
        # Local Space
        mmod.connectAttr(causeObj+".worldMatrix", matrixMult.name+".matrixIn[0]")
        mmod.connectAttr(self.root.name+".worldInverseMatrix", matrixMult.name+".matrixIn[1]")

        # Extracting World Matrix
        mmod.connectAttr(matrixMult.getMatrixSum(), decompWorldMatrix.getInputMatrix())

        # Delta Translation
        if (translationDirection>0):
                
            mmod.connectAttr(decompWorldMatrix.getOutputTranslate(), deltaTranslation.name+".input3D[0]")
            outTranslation =  mc.getAttr(decompWorldMatrix.getOutputTranslate())[0]
            mc.setAttr (deltaTranslation.name+".input3D[1]", outTranslation[0], outTranslation[1], outTranslation[2], type="double3")
            deltaTranslation.operation = 2
        else:
            
            mmod.connectAttr(decompWorldMatrix.getOutputTranslate(), deltaTranslation.name+".input3D[1]")
            outTranslation =  mc.getAttr(decompWorldMatrix.getOutputTranslate())[0]
            mc.setAttr (deltaTranslation.name+".input3D[0]", outTranslation[0], outTranslation[1], outTranslation[2], type="double3")
            deltaTranslation.operation = 2


        # Offset ------------- FINISH
        mmod.connectAttr (deltaTranslation.getOutput3D(), offset.name+".input3D[0]")
        # Distance Between Joints Upper and Lower
        upWorldY  = mc.xform(effectObj, q=True, ws=True, t=True)[1]
        lowWorldY = mc.xform(causeObj, q=True, ws=True, t=True)[1]
        # CHANGE TO RADIUS OFFSET
        mc.setAttr(offset.name+".input3D[1].input3Dy", -1*(abs(upWorldY - lowWorldY)-0.1))

        # Clamping Distance
        mmod.connectAttr(offset.getOutput3D(), clamp.getInput())
        clamp.maxG = 1000000
        clamp.minG = 0
        # Connecting to Ribbon Joint
        if (translationDirection>0):
            mmod.connectAttr(clamp.getOutputG(), effectObj+".translateY")
        else:
            # ReverseDirection
            mmod.connectAttr(clamp.getOutputG(), reversedDirection.getInput1())
            reversedDirection.input2 = -1
            mmod.connectAttr(reversedDirection.getOutput(), effectObj+".translateY" )

    def lipAutoMovement(self):
        autoMovementGuideGroup = mmod.transform(side=self.side, name=self.name+"AutoMovGuides", type="GRP", parent= self.parent)
        for i, (upper, lower) in enumerate(zip(self.upperControls, self.lowerControls)):
            # LOWER TO UPPER
            print lower, fn.getParent(lower), fn.getParent(upper)
            self.lipCollisionSetUp (fn.getParent(fn.getParent(lower)), fn.getParent(upper), self.root, translationDirection=1)
            self.lipCollisionSetUp (fn.getParent(fn.getParent(upper)), fn.getParent(lower), self.jawJnt, translationDirection=-1)

            



# mc.file(new=True, f=True)
# mc.file("C:/Users/anama/Desktop/MajorProject/Production/MPJ_MASTER/assets/character/rigging/Diana/wip/temp/dianaFace01.0019.ma", f=True, type="mayaAscii" )
dianaLips = lips(lipUpper="C_upperLip00_GRP", lipLower="C_lowerLip00_GRP", lipCorners="C_lipCorners00_GRP", root="C_headBase01_JNT", jawJNT="C_jaw00_JNT", parent="C_rig00_GRP")

# Scaling Down Joints Rad
mc.select ("C_*Lip*_JNT")
jntList = mc.ls(sl=True)
for jnt in jntList:
    mc.setAttr(jnt+".radius", 0.1)