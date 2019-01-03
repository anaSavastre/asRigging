import maya.cmds as mc
import maya.OpenMaya as om


# SelectionList

selection = mc.ls(sl=True)
# 1. Create a Selection List
mSel = om.MSelectionList()
mSel.add(selection)
