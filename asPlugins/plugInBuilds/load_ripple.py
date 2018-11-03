import maya.cmds as mc
import shutil 
import os 


plugIn = "asRipple"


releasePath = mc.loadPlugin("D:/Bournemouth University/asRigging/scripts/asRigging/tmpFiles/mayaApi/rippleDeformer.py")

pluginPath = "D:/Bournemouth University/asNodes"

if (mc.pluginInfo(pluginPath+"/"+plugIn, loaded=True, q=True)):
    mc.unloadPlugin(plugIn, f=True)

shutil.copy(releasePath, pluginPath)

# print "hello"
mc.loadPlugin(pluginPath+"/"+plugIn)
