
import maya.OpenMaya as om

import maya.cmds as mc
import maya.OpenMayaMPx as mpx
import maya.OpenMayaFX as omFX
import sys

commandName = "vParticle"

kHelpFlag = "-h"
kHelpLongFlag = "-help"
kSparseFlag = "s"
kSparseLongFlag = "sparse"
helpMessage = "this command is used to attach a particle on each vtx of the mesh"


class pluginCommand(mpx.MPxCommand):
    
    mObj_particle = om.MObject()
    sparse = None
    def __init__(self):
         mpx.MPxCommand.__init__(self)

    def argumentParser(self, argList):

        syntax  = self.syntax()
        try:
            parseArgument = om.MArgDatabase(syntax, argList)
        except:
            print "incorrect argument"
            return "unknown"
        if parseArgument.isFlagSet(kSparseFlag):
            self.sparse = parsedArgument.flagArgumentDouble(kSparseFlag, 0)
            return None
            # return om.MStatus.kSuccess
        if parseArgument.isFlagSet(kSparseLongFlag):
            self.sparse = parsedArgument.flagArgumentDouble(kSparseLongFlag, 0)
            # return om.MStatus.kSuccess
            return None

        if parseArgument.isFlagSet(kHelpFlag):
            self.setResult(helpMessage) 
            # return om.MStatus.kSuccess
            return None
        if parseArgument.isFlagSet(kHelpLongFlag):
            self.setResult(helpMessage)     
            # return om.MStatus.kSuccess
            return None

    def undoIt(self):
        mFnDagNode = OpenMaya.MFnDagNode(self.mObj_particle)
        mDagMod = OpenMaya.MDagModifier()
        if self.mObj_particle.apiTypeStr()!="kInvalid":
            mDagMod.deleteNode(mFnDagNode.parent(0))
            mDagMod.doIt()
            self.mObj_particle = OpenMaya.MObject()
        return None
        #return OpenMaya.MStatus.kSuccess
    
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
        # return om.MStatus.kSuccess
        return None


def commandCreator():
    return mpx.asMPxPtr(pluginCommand())

def syntaxCreator():
    # Create syntaxObject
    syntax = om.syntax()

    # Collect/add the flag
    syntax.addFlag(kHelpLongFlag, kHelpFlag)
    syntax.addFlag(kSparseLongFlag, kSparseFlag, om.syntax.kDouble)

    # return syntax
    return syntax 


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
