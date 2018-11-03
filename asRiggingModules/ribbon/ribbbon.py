import maya.cmds as mc
import functions as fn



mc.file(new = True, f=True)

class create:
    def printCreate(self):
        print "text function of class"
    def transform (self, prefix="C", name="locator", sufix="TRN", parent="0"):
        transform =mc.createNode("transform", n=prefix+"_"+name+"_"+sufix)
    def locator (self, prefix="C", name="locator", parent="0"):
        loc = mc.spaceLocator(name=prefix+"_"+name+"_LOC")
        if(parent!="0"):
            mc.parent(loc, parent)
        return loc

def createGuideLoc (numbLoc):
    locList = []
    k=0;
    for i in range (-numbLoc/2+1, numbLoc/2):
        loc = mc.spaceLocator(n="C_guideLoc0"+str(k)+"_LOC")[0]
        mc.xform(loc, t=[i, 0, 0])
        k+=1
        locList.append(loc)
    locGrp=mc.group(locList, n="C_guideLoc_GRP")
    return locGrp

def createMatloft (locList):
    matloft = mc.createNode("asMatloft", n="testMatloft")
    k=0
    for loc in locList:        
        mc.connectAttr(loc+".worldMatrix", matloft+".inputMatrix["+str(k+1)+"]")
        k+=1
    # Creating nrbSurface
    surface = mc.createNode("nurbsSurface")
    # Connecting surface
    mc.connectAttr(matloft+".outputSurface", surface+".create") 

    return matloft, surface

def createRivets (matfolt, numbInstances):
    for i in range (numbInstances):
        mc.createNode("asRivet", n="C_ribbon0"+str(i)+"_RVT")
        

#####################   Main    #####################

# Creating guides locators 
numbLoc = 10
locGrp = createGuideLoc(numbLoc)
# Create matLoft node
matloft, surface = createMatloft(mc.listRelatives(locGrp, c=True))
# Creating rivets along surface
createRivets(matloft, numbLoc)




# TEMPORARY
mc.hide(locGrp)

# loc = create().locator()


