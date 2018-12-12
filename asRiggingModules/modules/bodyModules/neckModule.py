import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import mayaNode as node
import asNodes as asNode

 
class neck(object):
    def __init__(self, side="C", name="neck" , neckJnt=None, root=None, parent=None, hook=None):
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
        self.forward = [0, -1, 0]
        self.up = [-1, 0, 0]
        mmod.resetCount() 
        # 1. CREATE JNT HIERARCHY
        # 1.0. HEAD
        self.headCtrl = rigFn.constructCTL(self.guides[-1], name = "head", parent = self.hook)
        # Rotation surfacePoints
        fn.rotateShapePoints(self.headCtrl.name, rotationVector=[0, 0, 90], pivot=mc.xform(self.guides[-1], q=True, ws=True, t=True))
        fn.translateShapePoints(self.headCtrl.name, [0, mc.getAttr(self.guides[-1]+".radius"), 0], pivot=mc.xform(self.guides[-1], q=True, ws=True, t=True))

                
        # # # 1.2. Neck FK
        # self.fkCtl1 = rigFn.constructCTL(self.guides[len(self.guides)/2-2], name = self.name+"FKCtl", parent = self.root)
        # self.fkCtl2 = rigFn.constructCTL(self.guides[len(self.guides)/2+2], name = self.name+"FKCtl", parent = self.fkCtl1)

        # 1.2. NECK RIBBON
        # Creating the Global Group
        self.neckGlobalGrp =  mmod.transform(side=self.side, name=self.name+"Global", type="GRP", parent=self.parent.rigGrp)
        # Create Surface Loft Guides
        # self.createLoftSurface(self.guides[1:-1])
        self.createLoftSurface(self.guides)
        # Attaching Joints
        self.attachJoinnts(parent=self.neckGlobalGrp)

        # # 2.0 TWIST INTERPOLATOR
        self.twistDeformation()
        # DELETING GUIDES
        mc.delete(self.guides)
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
    def twistDeformation(self):
        '''
        For Creating the twist deformation we need to duplicate the surface twice and apply all the transformations in local space and then apply
        them to the deformation surface through because otherwise we encounter double transformations 

        '''
        # Duplicating the surface

        matloftSurface = mc.duplicate(self.surface, name="C_neckSurfaceDeformation01_NRB", rc=True)[0]
        mc.rename( fn.getChildren(matloftSurface)[0], "C_neckSurfaceDeformationShape01_SHP" )
        twistSurface = mc.duplicate(self.surface, name="C_neckTwistDeformation01_NRB" , rc=True)[0]
        mc.rename( fn.getChildren(twistSurface)[0], "C_neckTwistDeformationShape01_NRB")

        # Reconnecting matloft
        mmod.connectAttr(self.matloftNode.getOutputSurface(), fn.getChildren(matloftSurface)[0]+".create")
        mc.disconnectAttr(self.matloftNode.getOutputSurface(), self.surface+".create")

        # Applying Twist Deformation
        # lowBound=-1, highBound=1, startAngle=0, endAngle=0
        twistHandle = mc.nonLinear(twistSurface, type="twist")
        # aimConstraint -offset 0 0 0 -weight 1 -aimVector 0 1 0 -upVector 0 0 1 -worldUpType "vector" -worldUpVector 0 1 0;
        mc.delete(mc.aimConstraint(self.headCtrl.name, twistHandle, aim=[0, 1, 0], u=[0, 0, 1]))
        mc.parent(twistHandle, self.surfaceGuidesGrp)
        twistHandle[0] = mc.rename(twistHandle[0], "C_neckTwistNode00_TWS")
        twistHandle[1] = mc.rename(twistHandle[1], "C_neckTwistHandle00_HND")

        # Applying the surfaces as blendShapes to the main surface
        self.bShpName = "C_neckDeformation_BSHP"
        bShp = mc.blendShape(matloftSurface,  self.surface, n=self.bShpName)
        mc.blendShape(bShp, edit=True, t=(fn.getParent(self.surface), 1, twistSurface, 1.0))
        # Making infuence 1
        mc.setAttr(self.bShpName+"."+matloftSurface, 1)
        mc.setAttr(self.bShpName+"."+twistSurface, 1)

        # Connecting the Twist Handke to ChestCTL and Pelvis Ctl
        multNode = mNode.multDoubleLinear(side=self.side, name=self.name+"ReverseRot")
        mmod.connectAttr(self.root.name+".rotateX", multNode.getInput1())
        mc.setAttr(multNode.getInput2(), -1)
        mmod.connectAttr(multNode.getOutput(), twistHandle[1]+".startAngle")
        
        multNode = mNode.multDoubleLinear(side=self.side, name=self.name+"ReverseRot")
        mmod.connectAttr(self.headCtrl.name+".rotateX", multNode.getInput1())
        mc.setAttr(multNode.getInput2(), -1)
        mmod.connectAttr(multNode.getOutput(), twistHandle[1]+".endAngle")

        # HIDING TWIST HANDLE
        mc.hide(twistHandle)

    def createLoftSurface(self, guides):
        self.surfaceGuides(guides)
        # Create surface from guides
        if (self.surfaceCtlPoints!=None):
            # Create matLoft node
            self.matloftNode = asNode.asMatloft(side=self.side, name=self.name+"Surface")
            # REVOLVE ORDER
            mc.setAttr(self.matloftNode.name+".revolveX", 1)
            mc.setAttr(self.matloftNode.name+".revolveZ", 0)

            for k, obj in enumerate(self.surfaceCtlPoints):
                mc.connectAttr(obj.name+".worldMatrix", self.matloftNode.name+".inputMatrix["+str(k)+"]")

            self.surface = mc.createNode("nurbsSurface", name="C_neckSurfaceShape00_SHP")
            mc.rename(fn.getParent(self.surface), "C_neckSurface00_NRB" )
            mc.parent (self.surface, self.surfaceGuidesGrp)
            # Connecting surface
            mc.connectAttr(self.matloftNode.getOutputSurface(), self.surface+".create") 

            # Creating the Controls
            # MIDDLE
            middleCtl = rigFn.constructCTL(self.surfaceOfsPoints[2], name = self.name+"IKmiddle", parent = fn.getParent(self.root))
            mc.delete(mc.listRelatives(middleCtl.name, c=True)[1])
            fn.scaleShapePoints(middleCtl.name, mc.getAttr(guides[len(guides)/2]+".radius"))
            fn.rotateShapePoints(middleCtl.name, rotationVector=mc.xform(guides[len(guides)/2], q=True, ws=True, ro=True), pivot=mc.xform(guides[len(guides)/2], q=True, ws=True, t=True))
            mc.parent(self.surfaceOfsPoints[2], middleCtl)
            # START
            mc.parentConstraint(self.root, self.surfaceOfsPoints[0], mo=True)
            # END
            mc.parentConstraint(self.headCtrl, self.surfaceOfsPoints[4], mo=True)
            # INBETWEEN POINTS
            # mc.parentConstraint(middleCtl, self.surfaceOfsPoints[1])
            # mc.parentConstraint(self.surfaceOfsPoints[0], self.surfaceOfsPoints[1])
            # mc.parentConstraint(middleCtl, self.surfaceOfsPoints[3])
            # mc.parentConstraint(self.surfaceOfsPoints[4], self.surfaceOfsPoints[3])
            self.influenceBlend(middleCtl, self.surfaceOfsPoints[0], self.surfaceOfsPoints[1])
            self.influenceBlend(middleCtl, self.surfaceOfsPoints[4], self.surfaceOfsPoints[3])
            
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

        for i in range (5):
            if (i==0):
                self.createRivet(0.030, parent=group)
            else:
                self.createRivet((i*2)/10.0, parent=group)
            

    def createRivet(self, parameterU, parent=None):
        rivet = asNode.asRivet(side=self.side, name=self.name)
        group = mmod.transform(side=self.side, name=self.name, type="GRP", parent=parent)
        # self.neckJnt.append(mmod.joint(side=self.side, name="bind"+self.name, parent= self.pelvisCtl))

        self.neckJnt.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent=self.neckJnt[-1] if len(self.neckJnt)>0 else self.root))
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
        mmod.connectAttr(self.neckJnt[-1].name+".parentInverseMatrix", matrixMult.name+".matrixIn[1]")
        decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name)
        mmod.connectAttr(matrixMult.getMatrixSum(), decompMatrix.getInputMatrix())
        mmod.connectAttr(decompMatrix.getOutputTranslate(), self.neckJnt[-1].name+".translate" )
        mmod.connectAttr(decompMatrix.getOutputRotate(), self.neckJnt[-1].name+".rotate" )
        mmod.connectAttr(decompMatrix.getOutputScale(), self.neckJnt[-1].name+".scale" )

