import maya.cmds as mc
import functions as fn
import mayaModule as mmod
import asNodes as asNode
import mayaNode as mNode


import rigFn as rigFn
import mayaNode as node


  
class spine(object):
    def __init__(self, side="C", name="spine" , spineJnt=None, root=None, parent=None):
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
        # self.spineJnt.append(mmod.joint(side=self.side, name="bind"+self.name, parent= self.pelvisCtl))

        self.spineJnt.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent=self.spineJnt[-1] if len(self.spineJnt)>0 else self.pelvisCtl))
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
            mc.setAttr(self.matloftNode.name+".revolveX", 1)
            mc.setAttr(self.matloftNode.name+".revolveZ", 0)

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