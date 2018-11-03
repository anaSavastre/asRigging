
import maya.OpenMaya as om

import maya.cmds as mc
import maya.OpenMayaMPx as mpx
import sys

commandName = "pluginCommand"

class pluginCommand(mpx.MPxCommand):
    def __init__(self):
         mpx.MPxCommand.__init__(self)

    def doIt(self, argList):
        print ("doIt....")


def commandCreator():
    return mpx.asMPxPtr(pluginCommand())

def initializePlugin(mObject):
    mplugin = mpx.MFnPlugin(mObject)
    try:
        mplugin.registerCommand(commandName, commandCreator)
    except:
        sys.stderr.write("Failed to register command: "+commandName)
def uninitializePlugin(mObject):
    mplugin = mpx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(commandName)
    except:
        sys.stderr.write("Failed to deregister command: "+commandName)
