import maya.cmds as mc
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import mayaNode as node
import asNodes as asNode

import ribbon as ribbon
class ribbonLimbs(object):
   
    def generateGuides(self):
        '''
        1. GET SEGMENT DIRECTION VECTOR
        2. NORMALIZE VECTOR
        3. CREATE GUIDES

        '''
        # 0. GLOBAL GROUP
        self.guideGrp = mmod.transform(side=self.side, name=self.name+"Guides", parent = self.parent, type="GRP")
        self.controlGrp = mmod.transform(side=self.side, name=self.name+"ControlGuides", parent = self.startJnt, type="GRP")
        mc.parent(self.controlGrp, self.guideGrp)

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
            group = mmod.transform(side=self.side, name=self.name+"Guide", type="GRP", parent=self.startJnt)
            # mc.parent(group, self.controlGrp)
            transformation =[] 
            for p0, v0 in zip(guide0, directionVector):
                transformation.append(p0+v0*(i*vectorLength/(self.numbGuides-1)))
            mc.xform(group, ws=True, t=transformation)
            # Creating Controller 
            ctrl = rigFn.constructCTL(group, side = self.side, name= self.name+"Control", parent = self.controlGrp, ctrlScale = vectorLength/15)
            self.guides.append(ctrl)

           

            mc.delete(group)

        # CONSTRAINING CONTROL GRP TO START JNT
        rigFn.parentConstraint(self.startJnt.name, fn.getParent(self.controlGrp.name), self.controlGrp.name)

    def rotationBlend(self, influence = mmod.transform(), child= mmod.transform(), blendValue = 0, index=0):
        # CREATING MATRIX MULTIPLICATION
        matrixMult = mNode.multMatrix(side=self.side, name="twistInterpolation"+str(index))
        decomposeMatrix = mNode.decomposeMatrix(side=self.side, name="twistValues"+str(index))
        mmod.connectAttr(influence.name+".worldMatrix", matrixMult.name+".matrixIn[0]")
        mmod.connectAttr(fn.getParent(fn.getParent(child))+".worldInverseMatrix", matrixMult.name+".matrixIn[1]")
        mmod.connectAttr(matrixMult.getMatrixSum(), decomposeMatrix.getInputMatrix())
        # CREATING INTERPOLATION
        divide = mNode.multDoubleLinear(side=self.side, name="twistInterpolation"+str(index))
        mmod.connectAttr(decomposeMatrix.name+".outputRotateX", divide.getInput1())
        mc.setAttr(divide.getInput2(), blendValue)
        mmod.connectAttr(divide.getOutput(), fn.getParent(child.name)+".rotateX")

    def twistInterpolation(self):
        # EXTRACT JOINT ROTATION - FROM END  TO START
        # num = len(self.guides)
        for i, guide in enumerate (self.guides[1:-1]):
            self.rotationBlend(influence = self.guides[-1], child= guide, blendValue =  1 - 0.25*(3-i), index = i)
            
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
        # 1. Get Local Transformation
        multMatrix1= mNode.multMatrix(side=self.side, name=self.name+"LocalSpaceMatrix1")
        multMatrix2= mNode.multMatrix(side=self.side, name=self.name+"LocalSpaceMatrix2")
        mmod.connectAttr(influence1+".worldMatrix", multMatrix1.name+".matrixIn[0]")
        mmod.connectAttr(fn.getParent(child)+".worldInverseMatrix", multMatrix1.name+".matrixIn[1]")
        mmod.connectAttr(influence1+".worldMatrix", multMatrix1.name+".matrixIn[0]")
        mmod.connectAttr(fn.getParent(child)+".worldInverseMatrix", multMatrix1.name+".matrixIn[1]")
        mmod.connectAttr(influence2+".worldMatrix", multMatrix2.name+".matrixIn[0]")
        mmod.connectAttr(fn.getParent(child)+".worldInverseMatrix", multMatrix2.name+".matrixIn[1]")
       
        
        # 2. DecomMatrix
        decompMatrix1 = mNode.decomposeMatrix(side=self.side, name=self.name+"Influence1")
        decompMatrix2 = mNode.decomposeMatrix(side=self.side, name=self.name+"Influence2")
        mmod.connectAttr(multMatrix1.getMatrixSum(), decompMatrix1.getInputMatrix())
        mmod.connectAttr(multMatrix2.getMatrixSum(), decompMatrix2.getInputMatrix())
        # 2. Average Sum
        average = mNode.plusMinusAverage(side=self.side, name=self.name+"Average")
        mmod.connectAttr(decompMatrix1.getOutputTranslate(), average.name+".input3D[0]")
        mmod.connectAttr(decompMatrix2.getOutputTranslate(), average.name+".input3D[1]")
        average.operation = 3
        # Connect Child
        mmod.connectAttr(average.getOutput3D(), child+".translate")
     
    def translationInterpolation(self):
       self.influenceBlend(influence1=self.guides[0].name, influence2=self.guides[2].name, child=fn.getParent(self.guides[1].name))
       self.influenceBlend(influence1=self.guides[-1].name, influence2=self.guides[2].name, child=fn.getParent(self.guides[-2].name))

    def __init__(self, side="C", name="ribbbonLimb", numberOfGuides=5, revolveVector= [1, 0, 0], endJnt=None, startJnt=None, parent=None, root=None):
        # self
        self.side = side
        self.name = name
        self.endJnt = endJnt
        self.startJnt = startJnt
        self.parent = parent
        self.root = root
        self.guides = []
        self.controlGrp = []
        self.numbGuides = numberOfGuides
        self.revolveVector=revolveVector
        # GLOBALS
        mmod.resetCount()
        # SET UP
        if (endJnt!=None, startJnt!=None):
            self.generateGuides()
            # CREATING THE RIBBONS
            ribbon.ribbon(side=self.side, name=self.name, guides=self.guides, revolveVector=self.revolveVector, parent=self.guideGrp, root=fn.getChhild(self.root)[0])

            # CREATING TWIST INTERPOLATION
            self.twistInterpolation()
            # CREATING TRANSLATION INTERPOLATION
            self.translationInterpolation()



