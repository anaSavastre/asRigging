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
            self.upperControls.append(rigFn.constructCTL(guide, name = "localUpperLip", parent = self.root, ctrlShape=6))
            # Sacling Child Joint Radius to 
            mc.setAttr(fn.getChildren(self.upperControls[-1])[-1]+".radius", 0.1)

        # Lower
        self.lowerControls = []
        for guide in self.lipLowerGuide:
            self.lowerControls.append(rigFn.constructCTL(guide, name = "localLowerLip", parent = self.jawJnt, ctrlShape=6))
            # Sacling Child Joint Radius to 
            mc.setAttr(fn.getChildren(self.upperControls[-1])[-1]+".radius", 0.1)


        # Upper Lip
        self.upperLipRibbon = ribbon.ribbon(name=self.name+"UpperRibbon", guides=self.upperControls, 
                            numberOfJoints=len(self.upperControls), revolveVector= [0, 0, 1], parent=self.parent, root=self.root)
        # LowerLip
        self.lowerLipRibbon = ribbon.ribbon(name=self.name+"LowerRibbon", guides=self.lowerControls, 
                            numberOfJoints=len(self.lowerControls), revolveVector= [0, 0, 1], parent=self.parent, root=self.jawJnt)

        # 3. CREATE LIP AUTO MOVEMENT
        self.lipAutoMovement ()

        # 4. CREATING CONTROLLER STRUCTURE


    def lipCollisionSetUp (self, guide, causeObj, effectObj, translationDirection=1, name="name"):
        # Create Necessary Nodes
        decompWorldMatrix = mNode.decomposeMatrix(side=self.side, name=name+"WM")
        deltaTranslation = mNode.plusMinusAverage(side=self.side, name=name+"DeltaTranslation")
        offset = mNode.plusMinusAverage(side=self.side, name=name+"Offset")
        clamp = mNode.clamp(side=self.side, name=name+"AutoMovClamp")
        if (translationDirection<0):
            reversedDirection = mNode.multDoubleLinear(side=self.side, name=name+"Reverse")
        
        # Extracting World Matrix
        mmod.connectAttr(guide+".worldMatrix", decompWorldMatrix.getInputMatrix())

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
        mc.setAttr(offset.name+".input3D[1].input3Dy", -1*(abs(upWorldY - lowWorldY)+0.1))

        # Clamping Distance
        mmod.connectAttr(offset.getOutput3D(), clamp.getInput())
        clamp.maxG = 1000000
        clamp.minG = 0
        # Connecting to Ribbon Joint
        if (translationDirection>0):
            mmod.connectAttr(clamp.getOutputG(), fn.getParent(effectObj)+".translateY")
        else:
            # ReverseDirection
            mmod.connectAttr(clamp.getOutputG(), reversedDirection.getInput1())
            reversedDirection.input2 = -1
            mmod.connectAttr(reversedDirection.getOutput(), fn.getParent(effectObj)+".translateY" )

    def lipAutoMovement(self):
        for i, (upper, lower) in enumerate(zip(self.upperControls, self.lowerControls)):
            # LOWER TO UPPER
            self.lipCollisionSetUp (fn.getChildren(lower)[-1], lower, upper, translationDirection=1)
            # self.lipCollisionSetUp (self.upperLipRibbon.ribbonJoints[i].name, upper, lower, translationDirection=-1, name=self.name+"Upper")

            # # Create Necessary Nodes
            # decompWorldMatrix = mNode.decomposeMatrix(side=self.side, name=self.name+"LowerWM")
            # deltaTranslation = mNode.plusMinusAverage(side=self.side, name=self.name+"LowerDeltaTranslation")
            # offset = mNode.plusMinusAverage(side=self.side, name=self.name+"LowerOffset")
            # clamp = mNode.clamp(side=self.side, name=self.name+"LowerAutoMovClamp")
           
            # # Extracting World Matrix
            # mmod.connectAttr(self.lowerLipRibbon.ribbonJoints[i].name+".worldMatrix", decompWorldMatrix.getInputMatrix())

            # # Delta Translation
            # mmod.connectAttr(decompWorldMatrix.getOutputTranslate(), deltaTranslation.name+".input3D[0]")
            # outTranslation =  mc.getAttr(decompWorldMatrix.getOutputTranslate())[0]
            # mc.setAttr (deltaTranslation.name+".input3D[1]", outTranslation[0], outTranslation[1], outTranslation[2], type="double3")
            # deltaTranslation.operation = 2

            # # Offset ------------- FINISH
            # mmod.connectAttr (deltaTranslation.getOutput3D(), offset.name+".input3D[0]")
            # # Distance Between Joints Upper and Lower
            # upWorldY  = mc.xform(upper, q=True, ws=True, t=True)[1]
            # lowWorldY = mc.xform(lower, q=True, ws=True, t=True)[1]
            # mc.setAttr(offset.name+".input3D[1].input3Dy", -1*abs(upWorldY - lowWorldY))

            # # Clamping Distance
            # mmod.connectAttr(offset.getOutput3D(), clamp.getInput())
            # clamp.maxG = 1000000
            # clamp.minG = 0
            # # Connecting to Ribbon Joint
            # mmod.connectAttr(clamp.getOutputG(), fn.getParent(upper)+".translateY")

            



# mc.file(new=True, f=True)
# mc.file("C:/Users/anama/Desktop/MajorProject/Production/MPJ_MASTER/assets/character/rigging/Diana/wip/temp/dianaFace01.0019.ma", f=True, type="mayaAscii" )
dianaLips = lips(lipUpper="C_upperLip00_GRP", lipLower="C_lowerLip00_GRP", lipCorners="C_lipCorners00_GRP", root="C_headBase01_JNT", jawJNT="C_jaw00_JNT", parent="C_rig00_GRP")

# Scaling Down Joints Rad
mc.select ("C_*Lip*_JNT")
jntList = mc.ls(sl=True)
for jnt in jntList:
    mc.setAttr(jnt+".radius", 0.1)