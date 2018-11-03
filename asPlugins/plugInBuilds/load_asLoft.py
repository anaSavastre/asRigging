import maya.cmds as mc
import shutil 
import os 

mc.file(new = True, f=True)

plugIn = "asMatloft"


releasePath = "D:/Bournemouth University/asRelease/" +plugIn + ".mll"
pluginPath = "D:/Bournemouth University/asNodes"

if (mc.pluginInfo(pluginPath+"/"+plugIn, loaded=True, q=True)):
    mc.unloadPlugin(plugIn, f=True)

shutil.copy(releasePath, pluginPath)

# print "hello"
mc.loadPlugin(pluginPath+"/"+plugIn)
