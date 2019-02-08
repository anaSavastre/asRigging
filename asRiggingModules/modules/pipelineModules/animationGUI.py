import maya.cmds as mc
import sys
import socket
import os 
from os import listdir
from functools import partial
from os.path import split, isfile, join, dirname

import pipeline as pl
import functions as fn
import mayaModule as mmod

class animationGUI (object):

    def __init__(self, dockUI=True):

        # GLOBALS
        self.windowName = "asAnimationGUI"
        self.workSpace = "asAnimationWorkSpace"
        self.dockControl = "asAnimationGUIDock"
        self.dock = dockUI
        self.windowWidth = 500
        self.windowHeight = 180
        self.animationGui()



    def animationGui(self):
        if mc.window(self.windowName, exists=True):
            mc.deleteUI(self.windowName, window=True)
        mc.window(self.windowName, title=self.windowName, widthHeight=(self.windowWidth, self.windowHeight), resizeToFitChildren=1)
        form = mc.formLayout()
        tabs = mc.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        mc.formLayout( form, edit=True, attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)) )
       
        ##############################################################################
        ##########################  Animation Retargeting   ##########################
        animationRetargetingTab = mc.rowColumnLayout("Animation Retargeting", numberOfColumns=4)
        mc.frameLayout( label='Driving Animation', collapsable=True, width=1000 )

        mc.rowColumnLayout(numberOfColumns=4, columnWidth=[(1, 70), (2, 150), (3, 80), (4, 150 )])
        mc.text (label = "Driver Joint", h=25)
        textField = mc.textField("driverJoint", tx="inset driver joint")
        mc.separator()

        mc.optionMenu( label='operation', w=100)#, changeCommand="self.printNewMenuItem")
        mc.menuItem( label='simpleBind' )
        mc.menuItem( label='seraratedBind' )
        mc.menuItem( label='aimBind' )

        ##########################  Animation Retargeting   ##########################
        ##############################################################################


        ##########################  DOCKING   ##########################

        # if mc.dockControl(self.dockControl, exists=True):
        #     mc.deleteUI(self.dockControl, control=True)
        # allowedAreas = ['right', 'left']
        # mc.dockControl( self.dockControl, area='right', content=self.windowName, allowedArea=allowedAreas )
        # # cmds.evalDeferred("cmds.dockControl('%s', e=True, r=True)" % self.dockCnt)  # for fuck sake Maya, raise the dock yourself!!
                
        ##########################  DOCKING   ##########################

        mc.showWindow(self.windowName)
        mc.window(self.windowName, e=True, widthHeight=(263, 180))


def cubeTesteScene():
    mc.file(new=True, f=True)
    path = "D:/Bournemouth University/CVA_Y3/Innovations/tests/"
    fn.loadLatestFile(path)
def customParentConstraint(parent, object):
    # Getting object parent
    objParent = fn.getParent(object)
    print objParent
    # Create Constraint Node
    asAnimationBinderNode = mc.createNode("asAnimationRetargeting")
    localOffset = fn.getLocalOffset(objParent, object)
    mc.setAttr(asAnimationBinderNode+".localOffset", [localOffset(i, j) for i in range(4) for j in range(4)], type="matrix")
    mmod.connectAttr(parent+".worldMatrix", asAnimationBinderNode+".parentWorldMatrix")
    mmod.connectAttr(objParent+".worldInverseMatrix", asAnimationBinderNode+".parentInverseMatrix")
    mmod.connectAttr(asAnimationBinderNode+".outRotation", object+".rotate")
    mmod.connectAttr(asAnimationBinderNode+".outTranslation", object+".translate")
    mmod.connectAttr(asAnimationBinderNode+".outScale", object+".scale")

# cubeTesteScene()
# customParentConstraint("customNodeConstraint|C_parentCube00_GRP1|C_parentCube01_CTL1", "customNodeConstraint|C_constraintCube00_GRP1")

animationGUIWindoe = animationGUI()