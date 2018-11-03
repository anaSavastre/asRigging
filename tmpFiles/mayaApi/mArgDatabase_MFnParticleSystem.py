
import maya.OpenMaya as om

import maya.cmds as mc
import maya.OpenMayaMPx as mpx
import maya.OpenMayaFX as omFX
import sys

commandName = "vertexParticle"

kHelpFlag = "-h"
kHelpLongFlag = "-help"
kSparseFlag = "-s"
kSparseLongFlag = "-sparse"
helpMessage = "this command is used to attach a particle on each vtx of the mesh"


class pluginCommand(mpx.MPxCommand):
    sparse = None
    def __init__(self):
         mpx.MPxCommand.__init__(self)

    def argumetnParser(self, argList):

        mSyntax  = self.syntax()
        parseArgument = om.MArgDatabase(mSyntax, argList)
        if parseArgument.isFlagSet(kSparseFlag):
            self.sparse = parsedArgument.flagArgumentDouble(kSparseFlag, 0)
            return om.MStatus.kSuccess
        if parseArgument.isFlagSet(kSparseLongFlag):
            self.sparse = parsedArgument.flagArgumentDouble(kSparseLongFlag, 0)
            return om.MStatus.kSuccess

        if parseArgument.isFlagSet(kHelpFlag):
            self.setResult(helpMessage) 
            return om.MStatus.kSuccess
        if parseArgument.isFlagSet(kHelpLongFlag):
            self.setResult(helpMessage)     
            return om.MStatus.kSuccess


    def redoIt(self):
        mSel = om.MSelectionList()
        mDagPath = om.MDagPath()
        mFnMesh = om.MFnMesh()
        om.MGlobal.getActiveSelectionList(mSel)
        if mSel.lenght()>=1:
            try:
                mSel.getDagPath(0, mDagPath)
                mFnMesh.setObject(mDagPath)

            except:
                print "select a polynesh"
                return om.MStatus.kUnknownParameter
        else:
            
                print "select a polynesh"
                return om.MStatus.kUnknownParameter


        mPointArray = om.MPointArray()
        mFnMesh.getPoints(mPointArray, om.MSapace,kWorlds)

        # Create a Particle System
        mFnPartice =  omFX.MFnParticleSystem()
        self.mObj_particle = mFnPartice.create()

        # To fix Maya Bug
        mFnPartice =  omFX.MFnParticleSystem(self.mObj_particle)


        counter = 0
        for i in range (mPointArray.lenght()):
            if i%self.sparse == 0:
                mFnPartice.emit(mPointArray[i])
                counter+=1
        print "totatl points: " +str(counter)
        mFnParticle.saveInitialState()
        return om.MStatus.KSuccess


    def doIt(self, argList):
        print ("doIt....")
        self.argumetnParser(argList)
        if self.sparce != None:
            self.redoIt()
        return om.MStatus.kSuccess


def commandCreator():
    return mpx.asMPxPtr(pluginCommand())

def syntaxCreator():
    # Create MSyntaxObject
    mSyntax = om.MSyntax()

    # Collect/add the flag
    mSyntax.addFlag(kHelpLongFlag, kHelpFlag)
    mSyntax.addFlag(kSparseLongFlag, kSparseFlag, om.MSyntax.kDouble)

    # return MSyntax
    return mSyntax 


def initializePlugin(mObject):
    mplugin = mpx.MFnPlugin(mObject)
    try:
        mplugin.registerCommand(commandName, commandCreator, syntaxCreator)
    except:
        sys.stderr.write("Failed to register command: "+commandName)
def uninitializePlugin(mObject):
    mplugin = mpx.MFnPlugin(mObject)
    try:
        mplugin.deregisterCommand(commandName)
    except:
        sys.stderr.write("Failed to deregister command: "+commandName)
