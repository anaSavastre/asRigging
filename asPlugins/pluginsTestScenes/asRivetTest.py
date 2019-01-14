import maya.cmds as mc

mc.file(new = True, f=True)


numbLoc = 3



# Create matLoft node
matloft = mc.createNode("asMatloft", n="testMatloft")
k=0;
for i in range (0, numbLoc):
    loc = mc.spaceLocator(n="loc"+str(k))[0]
    mc.xform(loc, t=[i*4, 0, 0])
    mc.connectAttr(loc+".worldMatrix", matloft+".inputMatrix["+str(k+1)+"]")
    k+=1
# mc.connectAttr(loc+".worldMatrix", matloft+".inMatrix")

# Creating nrbSurface
surface = mc.createNode("nurbsSurface")
# Connecting surface
mc.connectAttr(matloft+".outputSurface", surface+".create") 

