import maya.cmds as mc
import shutil 
import os 


plugIn = "asAnimationRetargeting"



pluginPath = "D:/Bournemouth University/asRigging/scripts/asRigging/asPlugins/plugins"

if (mc.pluginInfo(pluginPath+"/"+plugIn+".py", loaded=True, q=True)):
    mc.unloadPlugin(plugIn+".py", f=True)

mc.loadPlugin(pluginPath+"/"+plugIn+".py")
