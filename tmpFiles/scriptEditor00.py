# ''' Maya Api Tutorial '''

# ''' 4. MFnMesh MFnDependency MPlug: Plug '''

# import maya.OpenMaya as om

# import maya.cmds as mc
# import maya.OpenMayaMPx as mpx
# import sys
# import json 


# # mc.pluginCommand()
# def mFnExercise():

        
#     mc.file(new = True, f=True)

#     # Crating the plane
#     plane = mc.polyPlane( w= 10, h=15, sx=20, sy=25, ax=[0, 1, 0])

#     # API code

#     #  1. Creating selection list
#     mSelectionList = om.MSelectionList() 
#     mSelectionList.add("pPlane1")

#     #  2. Creating MObject and MDagPath
#     mObj = om.MObject() 
#     mDagPath = om.MDagPath()

#     # 3.Request dependency node
#     mSelectionList.getDependNode(0, mObj)
#     mSelectionList.getDagPath(0, mDagPath)

#     # print mDagPath.fullPathName()

#     # 4.MFnMesh data type: Mesh function set
#     mMesh = om.MFnMesh(mDagPath)
#     # print mMesh.fullPathName()

#     # 5.Dependency Node function set
#     mDependencyNode = om.MFnDependencyNode(mObj)

#     print mDependencyNode.name()

#     # 6.Get all the connections of a shape node
#     mPlugArray = om.MPlugArray()
#     mMesh.getConnections(mPlugArray)

#     # print mPlugArray.length()
#     # print mPlugArray[0].name()
#     # print mPlugArray[1].name()

#     mPlugArrayConnections = om.MPlugArray()
#     mPlugArray[1].connectedTo(mPlugArrayConnections, True, False)  

#     # print mPlugArrayConnections.length()
#     # print mPlugArrayConnections[0].name()
#     # print mPlugArrayConnections[0].name()

#     mObj2 = mPlugArrayConnections[0].node()
#     mDependencyNode2 =om.MFnDependencyNode(mObj2)
#     print mDependencyNode2.name()

#     planeWidth =  mDependencyNode2.findPlug("width")
#     planeHeight =  mDependencyNode2.findPlug("height")
#     planeSubWidth = mDependencyNode2.findPlug("subdivisionsWidth")
#     planeSubHeight = mDependencyNode2.findPlug("subdivisionsHeight")
#     print planeWidth.asInt()
#     print planeHeight.asInt()
#     print planeSubWidth.asInt()
#     print planeSubHeight.asInt()

#     planeSubWidth.setInt(10)
#     planeSubHeight.setInt(10)

# # shapeList=om.MSelectionList()
# # shapeList.add("curve1")
# # mObj = om.MObject() 
# # mDagPath = om.MDagPath()

# # # 3.Request dependency node
# # shapeList.getDependNode(0, mObj)
# # shapeList.getDagPath(0, mDagPath)

# # print mDagPath.fullPathName()
# # # shape = om.MFnDependencyNode(shapeList[0])

# # print mc.polyEvaluate()

# # boundingBox = om.MBoundingBox()
# # selectionList = mc.ls(sl=True)
# # print selectionList[0]
# # # print mc.selectType(selectionList[0], q=True)
# # # vtx = mc.polyInfo(selectionList, ev=True)
# # # print vtx
# # # str=selectionList[0].replace("C_KOA_body_PLY.e[", "[")
# # # print str
# # # for obj in selectionList:

# # import maya.cmds as mc

# # mc.loadPlugin("D:/Bournemouth University/asRigging/scripts/asRigging/tmpFiles/mayaApi/rippleDeformer.py")


# def reference():

#     # Build a sample scene:
#     # main scene contains a reference to mid.ma.
#     # mid.ma contains a reference to bot.ma.

#     # Create bot.ma with a poly sphere.
#     #
#     cmds.polySphere()
#     cmds.file( rename='bot.ma' )
#     cmds.file( f=True, s=True, type='mayaAscii')

#     # Create mid.ma with a poly cone.
#     # Reference bot.ma into mid.ma and group
#     # the sphere in bot.ma
#     #
#     cmds.file( f=True, new=True )
#     cmds.file( 'bot.ma', r=True,ns='bot' )
#     cmds.polyCone()
#     cmds.group( 'bot:pSphere1' )
#     cmds.file( rename='mid.ma' )
#     cmds.file( f=True, s=True, type='mayaAscii')

#     # Create a poly plane.
#     # Reference mid.ma into the main scene,
#     # move the cone in mid.ma, and connect
#     # the plane to the sphere in bot.ma.
#     #
#     cmds.file( f=True, new=True )
#     cmds.file( 'mid.ma', r=True, ns='mid' )
#     cmds.select( 'mid:pCone1', r=True )
#     cmds.move( 5, 5, 5, r=True )
#     cmds.polyPlane()
#     cmds.connectAttr( 'pPlane1.ty', 'mid:bot:polySphere1.radius' )



#     print cmds.referenceQuery( 'mid.ma', referenceNode=True )
#     # Result: midRN
#     print cmds.referenceQuery( 'C:/Users/anama/Documents/maya/projects/default/scenes/bot.ma', referenceNode=True)
#     # Result: mid:botRN
#     print cmds.referenceQuery( 'bot.ma', referenceNode=True, parent=True )
#     # Result: midRN
#     print cmds.referenceQuery( 'bot.ma', referenceNode=True, topReference=True )
#     # Result: midRN

   
        
# # reference()

# # DagFn instance
# dagFn = om.MFnDagNode()
# selectionListFn =om.MSelectionList()
# mObj = om.MObject()

# geoList = mc.ls(geometry=True)
# for geo in geoList:
#     selectionListFn.add(geo)
#     selectionListFn.getDependNode(0, mObj)
    
