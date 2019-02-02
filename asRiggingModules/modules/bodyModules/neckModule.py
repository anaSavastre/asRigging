import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import mayaNode as node
import asNodes as asNode


class neck(object):
    def __init__(self, side="C", name="neck" , revolveVector = [1, 0, 0], neckJnt=None, root=None, parent=None, hook=None):
        '''
        NECK MODULE

        1. CREATE JNT HIERARCHY
               > NECK RIBBON
               > HEAD
    
        '''
        
        # GLOBALS
        self.side = side
        self.name = name
        self.root = root
        self.parent = parent
        self.hook = hook
        self.guides = fn.descendentsList(root=neckJnt)
        self.neckJnt = []
        self.revolveVector = revolveVector
        mmod.resetCount() 
        # 1. CREATE JNT HIERARCHY
        # 1.0. HEAD
        self.headCtrl = rigFn.constructCTL(self.guides[-1], name = "head", parent = self.hook)
        # Rotation surfacePoints
        fn.rotateShapePoints(self.headCtrl.name, rotationVector=[0, 0, 90], pivot=mc.xform(self.guides[-1], q=True, ws=True, t=True))
        fn.translateShapePoints(self.headCtrl.name, [0, mc.getAttr(self.guides[-1]+".radius"), 0], pivot=mc.xform(self.guides[-1], q=True, ws=True, t=True))

        # 1.2. NECK RIBBON
        # Creating the Global Group
        self.neckGlobalGrp =  mmod.transform(side=self.side, name=self.name+"Global", type="GRP", parent=self.parent.rigGrp)
        # Extracting the forward and up vectors
        self.getRivetAlignmentVectors()
        # Create Surface Loft Guides
        self.createLoftSurface(self.guides[:-1])
        # Attaching Joints
        self.attachJoinnts(parent=self.neckGlobalGrp)

        # SPACE SWITCH FOR MIDDLE CONTROL
        self.middleCtrl.createSpaceSwitch()
        self.middleCtrl.addSpaceSwitch(spaceName= "chest", parentObject = self.root)
        
        # SPACE SWITCH FOR HEAD CONTROL
        self.headCtrl.createSpaceSwitch()
        self.headCtrl.addSpaceSwitch(spaceName= "middle", parentObject = self.middleCtrl)


        # DELETING GUIDES
        mc.delete(self.guides)
    
    def getRivetAlignmentVectors(self):
    
        # GETTING THE LOCAL SPACE OF THE ROOT JNT
        multMatrix = mNode.multMatrix(side=self.side, name=self.name+"ObjectSpace")
        mmod.connectAttr(self.root.name+".parentInverseMatrix", multMatrix.name+".matrixIn[0]")
        mmod.connectAttr(self.root.name+".worldMatrix", multMatrix.name+".matrixIn[1]")

        # Vector Product 
        forward = mNode.vectorProduct(side=self.side, name=self.name+"ForwardVector")
        up = mNode.vectorProduct(side=self.side, name=self.name+"UpVector")
        mc.setAttr(forward.getInput1(), 0, 1, 0, type="double3")
        mc.setAttr(up.getInput1(), 1, 0, 0, type="double3")
        forward.operation = 3
        up.operation = 3
        forward.normalizeOutput = 1
        up.normalizeOutput = 1
        mmod.connectAttr(multMatrix.getMatrixSum(), forward.name+".matrix")
        mmod.connectAttr(multMatrix.getMatrixSum(), up.name+".matrix")
        # Reverse Forward Vector
        revNode = mNode.multiplyDivide(side=self.side, name=self.name+"ReverseForwardVector")
        mc.setAttr(revNode.getInput2(), -1, -1, -1, type="double3")
        mmod.connectAttr(forward.getOutput(), revNode.getInput1())

        # OUTPUTS
        self.forward = revNode.getOutput() 
        self.up = up.getOutput()
    
    def createGuideFromObj(self, obj, parent=None):        
        ofs = mmod.transform(side=self.side, name=self.name+"offsetPoint", type="OFS", parent=parent)
        fn.align(obj, ofs)
        ctlPoint = mmod.transform(side=self.side, name=self.name+"ControlPoint", type="GRP", parent=ofs)
        self.surfaceOfsPoints.append(ofs)
        self.surfaceCtlPoints.append(ctlPoint)

    def surfaceGuides(self, guides):
        grp = mmod.transform(side=self.side, name=self.name+"SurfaceGuides", parent=self.neckGlobalGrp.name)
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

            self.surface = mc.createNode("nurbsSurface", name="C_neckSurfaceShape00_SHP")
            mc.rename(fn.getParent(self.surface), "C_neckSurface00_NRB" )
            mc.parent (self.surface, self.surfaceGuidesGrp)
            # Connecting surface
            mc.connectAttr(self.matloftNode.getOutputSurface(), self.surface+".create") 
            # REBUILD SURFACE FOR HIGHER DENSITY
            mc.rebuildSurface(self.surface, su=len(guides)+2, sv=1, kr=2)

            # Creating the Controls
            # MIDDLE
            middleCtl = rigFn.constructCTL(self.surfaceOfsPoints[2], name = self.name+"IKmiddle", parent = fn.getParent(self.root))
            mc.delete(mc.listRelatives(middleCtl.name, c=True)[1])
            fn.scaleShapePoints(middleCtl.name, mc.getAttr(guides[len(guides)/2]+".radius"))
            fn.rotateShapePoints(middleCtl.name, rotationVector=mc.xform(guides[len(guides)/2], q=True, ws=True, ro=True), pivot=mc.xform(guides[len(guides)/2], q=True, ws=True, t=True))
            mc.parent(self.surfaceOfsPoints[2], middleCtl)
            # START
            mc.parent(self.surfaceOfsPoints[1], self.surfaceOfsPoints[0])
            mc.parentConstraint(self.root, self.surfaceOfsPoints[0], mo=True)
            # END
            mc.parent(self.surfaceOfsPoints[3], self.surfaceOfsPoints[4])
            mc.parentConstraint(self.headCtrl, self.surfaceOfsPoints[4], mo=True)

            self.middleCtrl = middleCtl
            # # INBETWEEN POINTS
            # self.influenceBlend(middleCtl, self.surfaceOfsPoints[0], self.surfaceOfsPoints[1])
            # self.influenceBlend(middleCtl, self.surfaceOfsPoints[4], self.surfaceOfsPoints[3])
            
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
     
    def attachJoinnts(self, parent=None):
        group = mmod.transform(side=self.side, name=self.name+"BindJnt", type="GRP", parent=parent)

        for i in range (1, len(self.guides)-1):
            self.createRivet(i, parent=group)

    def createRivet(self, parameterU, parent=None):
        rivet = asNode.asRivet(side=self.side, name=self.name)
        group = mmod.transform(side=self.side, name=self.name, type="GRP", parent=parent)
        neckParent = mmod.transform(side=self.side, name="bind"+self.name.capitalize(), type="GRP", parent=self.root)
        fn.align(group, neckParent)
        self.neckJnt.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent= neckParent))
        rivet.parameterU = parameterU

        mmod.connectAttr(self.surface+".worldSpace", rivet.getInputSurface())
        mmod.connectPlugs(rivet.outRotation, group.rotate)
        mmod.connectPlugs(rivet.outTranslation, group.translate)
        mmod.connectAttr(parent.name+".worldInverseMatrix", rivet.name+".parentInverseMatrix")
        mmod.connectAttr(self.forward, rivet.name+".forward")
        mmod.connectAttr(self.up, rivet.name+".up")

        # GET GRP WORLD TRANSFORM
        matrixMult   = mNode.multMatrix(side=self.side, name=self.name)
        mmod.connectAttr(group.name+".worldMatrix", matrixMult.name+".matrixIn[0]")
        mmod.connectAttr(self.neckJnt[-1].name+".parentInverseMatrix", matrixMult.name+".matrixIn[1]")
        decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name)
        mmod.connectAttr(matrixMult.getMatrixSum(), decompMatrix.getInputMatrix())
        mmod.connectAttr(decompMatrix.getOutputTranslate(), self.neckJnt[-1].name+".translate" )
        mmod.connectAttr(decompMatrix.getOutputRotate() , self.neckJnt[-1].name+".rotate" )
        mmod.connectAttr(self.root.name+".scale", self.neckJnt[-1].name+".scale" )
      
