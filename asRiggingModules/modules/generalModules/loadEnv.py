import maya.cmds as mc
import shutil 
import os 
import sys

# print sys.path
plugInList = ["asRivet", "asMatloft", "asTrig"]
controlShapesPath = "D:/Bournemouth University/asRigging/controlShapes"

def loadEnvironment():
    sys.path.append("D:/Bournemouth University/asRigging/scripts/asRigging/asRiggingModules/functions")
    sys.path.append("D:/Bournemouth University/asRigging/scripts/asRigging/asRiggingModules/modules/generalModules")
    sys.path.append("D:/Bournemouth University/asRigging/scripts/asRigging/asRiggingModules/modules/bodyModules")

    loadPlugins()
def loadPlugins():
    for plugIn in plugInList:
        releasePath = "D:/Bournemouth University/asRelease/" +plugIn + ".mll"
        pluginPath = "D:/Bournemouth University/asNodes"
        if (mc.pluginInfo(pluginPath+"/"+plugIn, loaded=True, q=True)):
            mc.unloadPlugin(plugIn, f=True)
        shutil.copy(releasePath, pluginPath)
        # print "hello"
        mc.loadPlugin(pluginPath+"/"+plugIn)

loadEnvironment()
