import maya.cmds as mc
import functions as fn
import mayaModule as mmod
import asNodes as asNode
import mayaNode as mNode


import rigFn as rigFn
import mayaNode as node

# New File
mc.file(new = True, f=True)


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
    def createRivet(self, parameterU, parent=None):
        rivet = asNode.asRivet(side=self.side, name=self.name)
        group = mmod.transform(side=self.side, name=self.name, type="GRP", parent=parent)
        spineParent = mmod.transform(side=self.side, name="bind"+self.name.capitalize(), type="GRP", parent=self.root)
        fn.align(group, spineParent)
        self.ribbonJoints.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent= spineParent))
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
        mmod.connectAttr(self.ribbonJoints[-1].name+".parentInverseMatrix", matrixMult.name+".matrixIn[1]")
        decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name)
        mmod.connectAttr(matrixMult.getMatrixSum(), decompMatrix.getInputMatrix())
        mmod.connectAttr(decompMatrix.getOutputTranslate(), self.ribbonJoints[-1].name+".translate" )
        mmod.connectAttr(decompMatrix.getOutputRotate() , self.ribbonJoints[-1].name+".rotate" )
        mmod.connectAttr(self.root.name+".scale", self.ribbonJoints[-1].name+".scale" )
       
    def attachJoinnts(self, parent=None):
        group = mmod.transform(side=self.side, name=self.name+"BindJnt", type="GRP", parent=parent)

        for i in range (1, len(self.guides)-1):
            self.createRivet(i, parent=group)
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

    def createLoftSurface(self):
        # Create surface from guides
        if (self.guides!=None):
            # Create matLoft node
            self.matloftNode = asNode.asMatloft(side=self.side, name=self.name+"Surface")
            # REVOLVE ORDER
            mc.setAttr(self.matloftNode.name+".revolveVector", self.revolveVector[0], self.revolveVector[1], self.revolveVector[2], type="double3")

            for k, obj in enumerate(self.guides):
                mc.connectAttr(obj.name+".worldMatrix", self.matloftNode.name+".inputMatrix["+str(k)+"]")

            self.surface = mc.createNode("nurbsSurface", name="C_spineSurfaceShape00_SHP")
            mc.rename(fn.getParent(self.surface), "C_spineSurface00_NRB" )
            mc.parent (self.surface, self.surfaceGuidesGrp)
            
            # CREATING SURFACE
            mc.connectAttr(self.matloftNode.getOutputSurface(), self.surface+".create") 
            # REBUILD SURFACE FOR HIGHER DENSITY
            mc.rebuildSurface(self.surface, su=self.numberOfJoints+2, sv=1, kr=2)

            # Creating the Controls
            # # MIDDLE
            # middleCtl = rigFn.constructCTL(self.surfaceOfsPoints[2], name = self.name+"IKmiddle", parent = self.fkCtl1)
            # mc.delete(mc.listRelatives(middleCtl.name, c=True)[1])
            # fn.scaleShapePoints(middleCtl.name, mc.getAttr(guides[len(guides)/2]+".radius"))
            # fn.rotateShapePoints(middleCtl.name, rotationVector=mc.xform(guides[len(guides)/2], q=True, ws=True, ro=True), pivot=mc.xform(guides[len(guides)/2], q=True, ws=True, t=True))
            # mc.parent(self.surfaceOfsPoints[2], middleCtl)

            # # # START
            # mc.parent(self.surfaceOfsPoints[1], self.surfaceOfsPoints[0])
            # mc.parentConstraint(self.pelvisCtl, self.surfaceOfsPoints[0], mo=True)
            # # # END
            # mc.parent(self.surfaceOfsPoints[3], self.surfaceOfsPoints[4])
            # mc.parentConstraint(self.chestCtl, self.surfaceOfsPoints[4], mo=True)
     
    def __init__(self, side="C", name="ribbon", guides=None, numberOfJoints=5, revolveVector= [1, 0, 0], parent=None, root=None):
        # GLOBALS
        asNode.asRivet.elemIndex=0
        asNode.asMatloft.elemIndex=0
        mmod.resetCount()

        self.side=side
        self.name = name
        self.parent = parent
        self.root =root
        self.guides = guides
        self.revolveVector = revolveVector
        self.ribbonJoints=[]
        self.numberOfJoints = numberOfJoints
        if (guides!=None):
            # Creating the Global Group
            self.ribbonGlobalGrp =  mmod.transform(side=self.side, name=self.name+"Global", type="GRP")#, parent=self.parent)
            self.surfaceGuidesGrp = mmod.transform(side=self.side, name=self.name+"SurfaceGuides")#, parent=self.spineGlobalGrp.name)
            # Extracting the forward and up vectors
            self.getRivetAlignmentVectors()
            # Create Surface Loft Guides
            self.createLoftSurface()   
            # matloftNode = loftSurfaceFromGuides(side=side, name=name, guides=guides)
            # Attaching Joints
            self.attachJoinnts(parent=self.ribbonGlobalGrp)
           

def testProject():
    guides = createGuides("C", 3, spacing=3)
    asRibbon = ribbon(guides=guides, numberOfJoints=5)

testProject()