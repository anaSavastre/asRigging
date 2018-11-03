import maya.OpenMaya as om

# Create dag Iterator
dagIterator = om.MItDag(om.MItDag.kDepthFirst, om.MFn.kInvalid)
dagNodeFn = om.MFnDagNode()

while (not dagIterator.isDone()):
    currentObj = dagIterator.currentItem()
    depth = dagIterator.depth()
    dagNodeFn.setObject(currentObj)

    name = dagNodeFn.name()
    type = currentObj.apiTypeStr()
    path = dagNodeFn.fullPathName()

    # print name
    # print type
    # print path

    printOut=""
    for i in range (depth):
        printOut+= "----->"
    printOut+=name+" : "+type+" : "

    print printOut
    dagIterator.next ()