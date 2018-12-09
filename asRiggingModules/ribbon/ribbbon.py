import maya.cmds as mc
import mayaModule as mmod
import asNodes as asNode


# New File
mc.file(new = True, f=True)


def createGuides(side, numberOfGuides):
    mmod.locator.elemIndex=0
    guideList=[]
    for i in range (numberOfGuides):
        guideList.append(mmod.locator(side=side, name= "locGuide"))
        mc.xform(guideList[i], t=[i, 0, 0])
    return guideList

def loftSurfaceFromGuides(side="C",name="matloft",guides=None):    
    if (guides!=None):
            
        # Create matLoft node
        matloft = asNode.asMatloft(side=side, name=name)

        for k, obj in enumerate(guides):
            mc.connectAttr(obj.name+".worldMatrix", matloft.name+".inputMatrix["+str(k)+"]")
        return matloft


class ribbon(object):
    def __init__(self, side="C", name="ribbon", guides=None):
        # GLOBALS
        asNode.asRivet.elemIndex=0
        asNode.asMatloft.elemIndex=0
        mmod.resetCount()

        self.side=side
        self.name = name
        if (guides!=None):
            matloftNode = loftSurfaceFromGuides(side=side, name=name, guides=guides)
        
        # For VISUALIZATION        
        surface = mc.createNode("nurbsSurface")
        # Connecting surface
        mc.connectAttr(matloftNode.getOutputSurface(), surface+".create") 

        # RIVETS
        numbGuides = len(guides)
        for i in range (numbGuides-1):
            rivet = asNode.asRivet(side=self.side, name=self.name)
            group = mmod.transform(side=self.side, name=self.name)
            rivet.percentage = 1
            coef = 1.0/(numbGuides*2.0)
            rivet.parameterU = coef*(i*2+1)
            mmod.connectPlugs(matloftNode.outputSurface, rivet.inputSurface)
            mmod.connectPlugs(rivet.outRotation, group.rotate)
            mmod.connectPlugs(rivet.outTranslation, group.translate)
            mc.setAttr(rivet.name+".forward", 0, 1, 0, type="double3")
            mc.setAttr(rivet.name+".up", 1, 0, 0, type="double3")



def testProject():
    guides = createGuides("C", 9)
    asRibbon = ribbon(guides=guides)

testProject()