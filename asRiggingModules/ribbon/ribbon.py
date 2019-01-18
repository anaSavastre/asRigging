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
            self.ribbonBind =  mmod.transform(side=self.side, name=self.name+"Global", type="GRP", parent=self.root)
            self.surfaceGuidesGrp = mmod.transform(side=self.side, name=self.name+"SurfaceGuides", parent=self.parent)
            # Extracting the forward and up vectors
            self.getRivetAlignmentVectors()
            # Create Surface Loft Guides
            self.createLoftSurface()   
            # Attaching Joints
            self.attachJoinnts(parent=self.surfaceGuidesGrp)
    def getRivetAlignmentVectors(self):
        # GETTING LOCAL SPACE OF ROOT
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

            self.surface = mc.createNode("nurbsSurface", name= self.side+"_"+self.name+"Surface00_SHP")
            mc.rename(fn.getParent(self.surface), self.side+"_"+self.name+"Surface00_NRB" )
            mc.parent (self.surface, self.surfaceGuidesGrp)
            
            # CREATING SURFACE
            mc.connectAttr(self.matloftNode.getOutputSurface(), self.surface+".create") 
            # REBUILD SURFACE FOR HIGHER DENSITY
            mc.rebuildSurface(self.surface, su=self.numberOfJoints+2, sv=1, kr=2)

          
     
    def createRivet(self, parameterU, parent=None):
        rivet = asNode.asRivet(side=self.side, name=self.name)
        group = mmod.transform(side=self.side, name=self.name, type="GRP", parent=parent)
        ribbonParent = mmod.transform(side=self.side, name="bind"+self.name.capitalize(), type="GRP", parent=self.ribbonBind)
        fn.align(group, ribbonParent)
        self.ribbonJoints.append(mmod.joint(side=self.side, name="bind"+self.name.capitalize(), parent= ribbonParent))
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

        for i in range (0, self.numberOfJoints+1):
            self.createRivet(i, parent=group)
        