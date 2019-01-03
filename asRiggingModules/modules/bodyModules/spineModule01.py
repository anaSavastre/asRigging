import maya.cmds as mc
import functions as fn
import mayaModule as mmod
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
        print "spineModule"
        # GLOBALS
        self.side = side
        self.name = name
        self.root = root
        self.parent = parent
        self.guides = fn.descendentsList(root=spineJnt)
        mmod.resetCount() 
        # 1. CREATE JNT HIERARCHY
        # 1.0. PELVIS
        self.pelvisCtl = rigFn.constructCTL(self.guides[0], name = "pelvis", parent = self.root)
        # 1.1. CHEST
        self.chestCtl = rigFn.constructCTL(self.guides[-1], name="chest", parent = self.root)
        # 1.2. SPINE RIBBON
        # Create Surface Loft Guides
        self.createLoftSurface(self.guides[1:-1])
        # DELETING GUIDES
        mc.hide(self.guides)

    def createLoftSurface(self, guides):
        self.surfaceGuides(guides)
        # Create surface from guides
        if (self.surfaceCtlPoints!=None):
            # Create matLoft node
            matloftNode = asNode.asMatloft(side=self.side, name=self.name+"Surface")
            # REVOLVE ORDER
            mc.setAttr(matloftNode.name+".revolveX", 1)
            mc.setAttr(matloftNode.name+".revolveZ", 0)

            for k, obj in enumerate(self.surfaceCtlPoints):
                mc.connectAttr(obj.name+".worldMatrix", matloftNode.name+".inputMatrix["+str(k)+"]")

            self.surface = mc.createNode("nurbsSurface")
            mc.parent (self.surface, self.surfaceGuidesGrp)
            # Connecting surface
            mc.connectAttr(matloftNode.getOutputSurface(), self.surface+".create") 

            # Creating the Controls
            # for obj in range(self.)
            # MIDDLE
            # Odd Number of guides
            gLen = len(guides)
            if (gLen%2!=0):
                middleCtl = rigFn.constructCTL(guides[(gLen/2)], name = self.name+"IKmiddle", parent = self.surfaceGuidesGrp)
                mc.delete(mc.listRelatives(middleCtl.name, c=True)[1])
                # mc.parent(self.surfaceOfsPoints[(gLen/2)],self.surfaceOfsPoints[(gLen/2+1)], self.surfaceOfsPoints[(gLen/2-1)], middleCtl)

                mc.parent(self.surfaceOfsPoints[(gLen/2)], middleCtl)
            # Even number of guides
            else:
                midGuide = mmod.transform()
                middleCtl = rigFn.constructCTL(guides[gLen/2-1], name = self.name+"IKmiddle", parent = self.surfaceGuidesGrp)

                mc.select(guides[gLen/2-1], guides[gLen/2], fn.getParent(middleCtl.name))
                fn.alignTool()
                # print 
                mc.delete(mc.listRelatives(middleCtl.name, c=True)[1], midGuide)
                mc.parent(self.surfaceOfsPoints[(gLen/2)-1], self.surfaceOfsPoints[(gLen/2)], middleCtl)
            
            # INFLUENCE INTERSECTION POINT9
            intPoint = (gLen/2-2)/2+1
            print intPoint
            print gLen
            # Ends
            for i in range (1, intPoint):
                self.gradientInfluence(parent = self.surfaceOfsPoints[i-1], child = self.surfaceOfsPoints[i])
                self.gradientInfluence(parent = self.surfaceOfsPoints[gLen-i], child = self.surfaceOfsPoints[gLen-i-1])
            # Middle
            for i in range (((gLen-1)/2)-1, intPoint, -1):
                self.gradientInfluence(parent=self.surfaceOfsPoints[i+1], child=self.surfaceOfsPoints[i])
                self.gradientInfluence(parent=self.surfaceOfsPoints[gLen-i-2], child=self.surfaceOfsPoints[gLen-i-1])
            # Intersection Point
            self.influenceBlend(self.surfaceOfsPoints[intPoint-1], self.surfaceOfsPoints[intPoint+1], self.surfaceOfsPoints[intPoint]) 
            self.influenceBlend(self.surfaceOfsPoints[gLen-intPoint-2], self.surfaceOfsPoints[gLen-intPoint], self.surfaceOfsPoints[gLen-intPoint-1]) 

            # # START
            mc.parentConstraint(self.pelvisCtl, self.surfaceOfsPoints[0], mo=True)
            # # END
            mc.parentConstraint(self.chestCtl, self.surfaceOfsPoints[gLen-1], mo=True)
            
    # def parentConstraint(self, parent=mmod.transform(), child=mmod.transform()):
    #     '''
    #     '''
    #     # 1. GET CHILD OFFSET
    #     childWM = mc.getAttr(child.name+".worldMatrix")
    #     print childWM
    #     # 2. MATRIX MULTIPLICATION 
    #     # 3. DECOMPOSE TRANSFORMATION
    #     # 4. CONSTRAINT CHILD
    
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

    def surfaceGuides(self, guides):
        grp = mmod.transform(side=self.side, name=self.name+"SurfaceGuides", parent=self.parent.rigGrp.name)
        self.surfaceGuidesGrp = grp
        self.surfaceOfsPoints = []
        self.surfaceCtlPoints = []
        mmod.resetTRNCount()
        for i, obj in enumerate(guides):
            localGrp =  mmod.transform(side=self.side, name=self.name+"offsetPoint", type="OFS", parent=grp)
            ofs = mmod.transform(side=self.side, name=self.name+"offsetPoint", type="OFS", parent=localGrp)
            # Matching orientation GUIDE > OFS
            fn.align(obj, ofs)
            ctlPoint = mmod.transform(side=self.side, name=self.name+"ControlPoint", type="GRP", parent=ofs)
            self.surfaceOfsPoints.append(ofs)
            self.surfaceCtlPoints.append(ctlPoint)
