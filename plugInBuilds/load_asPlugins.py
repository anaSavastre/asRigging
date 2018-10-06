import maya.cmds as mc
import shutil 
import os 


plugInList = ["asRivet", "asMatloft", "asTrig"]


for plugIn in plugInList:
    releasePath = "D:/Bournemouth University/asRelease/" +plugIn + ".mll"
    pluginPath = "D:/Bournemouth University/asNodes"
    if (mc.pluginInfo(pluginPath+"/"+plugIn, loaded=True, q=True)):
        mc.unloadPlugin(plugIn, f=True)
    shutil.copy(releasePath, pluginPath)
    # print "hello"
    mc.loadPlugin(pluginPath+"/"+plugIn)
