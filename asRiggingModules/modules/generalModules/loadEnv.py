import maya.cmds as mc
import shutil 
import os 
import sys
import socket
# print sys.path
plugInList = ["asRivet", "asMatloft", "asTrig"]
hostName = socket.gethostname()

if (hostName == "DESKTOP-4NJ3EJ0"):
    asRigging = "D:/Bournemouth University/asRigging/scripts/asRigging"
    controlShapesPath = asRigging+"/controlShapes"
if (hostName == "DESKTOP-CM0E2QL"):
    asRigging = "C:/Users/Kari Noriy/Desktop/Ana/asRigging/scripts/asRigging"
    controlShapesPath = asRigging+"/controlShapes"
if (hostName == "DESKTOP-PQV0HOV"):
    asRigging = "C:/Users/AnaMaria/Documents/asRigging/scripts/asRigging"
    controlShapesPath = asRigging+"/controlShapes"

def loadEnvironment():

    sys.path.append(asRigging+"/asRiggingModules/functions")
    sys.path.append(asRigging+"/asRiggingModules/modules/generalModules")
    sys.path.append(asRigging+"/asRiggingModules/modules/bodyModules")
    sys.path.append(asRigging+"/asRiggingModules/modules/faceModules")
    sys.path.append(asRigging+"/asRiggingModules/controls")
    
    loadPlugins()
def loadPlugins():
    for plugIn in plugInList:
        #releasePath = "D:/Bournemouth University/asRelease/" +plugIn + ".mll"
        pluginPath = ""
        if (hostName == "DESKTOP-4NJ3EJ0"):
            pluginPath = "D:/Bournemouth University/asNodes"
        if (hostName == "DESKTOP-CM0E2QL"):
            pluginPath = "C:/Users/Kari Noriy/Desktop/Ana/asNodes"
        if (hostName == "DESKTOP-PQV0HOV"):
            pluginPath = "C:/Users/AnaMaria/Documents/asNodes"

        if (mc.pluginInfo(pluginPath+"/"+plugIn, loaded=True, q=True)):
            mc.unloadPlugin(plugIn, f=True)
        #shutil.copy(releasePath, pluginPath)
        mc.loadPlugin(pluginPath+"/"+plugIn)

loadEnvironment()
