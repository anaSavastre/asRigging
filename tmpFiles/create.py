import maya.cmds as mc
import maya.OpenMaya as om

# class transform

def getDagPath(node=None):
    selectionList = om.MSelectionList();
    selectionList.add(node)
    dagPath = om.MDagPath()
    selectionList.getDagPath(0, dagPath)
    return dagPath

attr = om.MObject
dagPath = getDagPath("C_globalMove00_CTL")
# print dagPath.fullPathName()
mNode = dagPath.node()

dependencyNode = om.MFnDependencyNode(mNode)
