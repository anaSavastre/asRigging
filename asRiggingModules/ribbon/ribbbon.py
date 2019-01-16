import maya.cmds as mc
import mayaModule as mmod
import asNodes as asNode


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
        mmod.connectAttr(self.spineJnt[-1].name+".parentInverseMatrix", matrixMult.name+".matrixIn[1]")
        decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name)
        mmod.connectAttr(matrixMult.getMatrixSum(), decompMatrix.getInputMatrix())
        mmod.connectAttr(decompMatrix.getOutputTranslate(), self.spineJnt[-1].name+".translate" )
        mmod.connectAttr(decompMatrix.getOutputRotate() , self.spineJnt[-1].name+".rotate" )
        mmod.connectAttr(self.root.name+".scale", self.spineJnt[-1].name+".scale" )
    
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
    def __init__(self, side="C", name="ribbon", guides=None, numberOfJoints=5, revolveVector= [1, 0, 0], parent=None, root=None):
        # GLOBALS
        asNode.asRivet.elemIndex=0
        asNode.asMatloft.elemIndex=0
        mmod.resetCount()

        self.side=side
        self.name = name
        self.parent = parent
        self.root =root
        self.revolveVector = revolveVector
        self.ribbonJoints=[]
        if (guides!=None):
            self.getRivetAlignmentVectors()
            matloftNode = loftSurfaceFromGuides(side=side, name=name, guides=guides)

            # For VISUALIZATION        
            self.surface = mc.createNode("nurbsSurface")
            # Connecting surface
            mc.connectAttr(matloftNode.getOutputSurface(), self.surface+".create") 
            mc.rebuildSurface(self.surface, su=len(guides)*2, sv=1, kr=2)

            # RIVETS
            numbGuides = len(guides)
            parentGroup = mmod.transform(side=self.side, name=self.name+"Joints", parent = self.parent)
            for i in range (numbGuides-1):
                coef = 1.0/(numbGuides*2.0)
                self.createRivet(coef*(i*2+1), parent=parentGroup)



            
                # rivet = asNode.asRivet(side=self.side, name=self.name)
                # group = mmod.transform(side=self.side, name=self.name, parent=parentGroup)
                # rivet.percentage = 1
                # coef = 1.0/(numbGuides*2.0)
                # rivet.parameterU = coef*(i*2+1)
                # mmod.connectAttr(surface+".worldSpace", rivet.getInputSurface())
                # mmod.connectPlugs(rivet.outRotation, group.rotate)
                # mmod.connectPlugs(rivet.outTranslation, group.translate)
                # mc.setAttr(rivet.name+".forward", 0, 1, 0, type="double3")
                # mc.setAttr(rivet.name+".up", 1, 0, 0, type="double3")
                # # Parent Inverse Matrix
                # mmod.connectAttr(parentGroup.name+".worldInverseMatrix", rivet.name+".parentInverseMatrix")
                # # Creating the joints
                # joint = mmod.joint(name=self.name, side=self.side, parent=group)

def testProject():
    guides = createGuides("C", 3, spacing=3)
    asRibbon = ribbon(guides=guides, numberOfJoints=5)

testProject()