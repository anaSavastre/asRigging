import maya.cmds as mc
import maya.OpenMaya as om
import shutil 
import os 
import sys
import mayaModule as mmod
import functions as fn
import pipeline 


# print sys.path
plugInList = ["asRivet", "asMatloft", "asTrig"]
controlShapesPath = "D:/Bournemouth University/asRigging/controlShapes"


# def loadComponents():


def folderHierarchy(projectEnv, rigName):
    # Creating Folder structures
    ''' rigging>CharacterName>
                    > RIG
                        >rigVersions.ma
                    > wip
                        >rigWip
                        >components
                        >controlShapes
                        >skinWeights

    '''
    rigEnv = projectEnv+"/rigging/"
    characterRigFolder = rigEnv + rigName
    if not os.path.exists(characterRigFolder):
        os.makedirs(characterRigFolder)
    # Rigging
    finalRig = characterRigFolder + "/RIG"
    if not os.path.exists(finalRig):
        os.makedirs(finalRig)
    # Work in progress
    wipProject = characterRigFolder + "/wip"
    if not os.path.exists(wipProject):
        os.makedirs(wipProject)
    # Component, controlShapes, skinWeights
    rigWip = wipProject+"/rigWip"
    if not os.path.exists(rigWip):
        os.makedirs(rigWip)
    componentsFile = wipProject+"/components"
    if not os.path.exists(componentsFile):
        os.makedirs(componentsFile)
    controlShapesFile = wipProject+"/controlShapes"
    if not os.path.exists(controlShapesFile):
        os.makedirs(controlShapesFile)
    skinWeightsFile = wipProject+"/skinWeights"
    if not os.path.exists(skinWeightsFile):
        os.makedirs(skinWeightsFile)

    # Create default ma files
    # Components
    file = mc.file(new = True, f=True)
    pipeline.saveFile(projectEnv=componentsFile, saveName=rigName+"Components")

    return rigWip, componentsFile, controlShapesFile, skinWeightsFile

def createJointHY(side, name, parent):
    grp = mmod.transform(side=side, name=name, type="GRP", parent=parent)
    ofs = mmod.transform(side=side, name=name, type="OFS", parent=grp)
    # loading ctrl
    objInScene = mc.ls("*_CTL")
    mc.file(controlShapesPath+"/"+name+"Control.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)
    newObjInScene = mc.ls("*_CTL")
    if (len(newObjInScene)-len(objInScene)==1):
        ctrl= [obj for obj in newObjInScene if obj not in objInScene]
    mc.parent(ctrl, ofs)
    return ctrl
    

class rigSceneSetup(object):
    def loadLatestFile(self, path):
        '''
        This function gets all the files in the given directory and loads the latest maya scene file
        '''
        files= os.listdir(path)
        latestFile = sorted(files)[-1];
        
        mc.file( path+"/"+latestFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)



    
    def getGeoBoundingBox(self):

        geoList = mc.ls(geometry=True)
        bBoxList = mc.polyEvaluate(geoList, boundingBox = True)
        minCourner = om.MPoint()
        maxCourner = om.MPoint()
        
        minCourner.x = bBoxList[0][0]
        minCourner.y = bBoxList[1][0]
        minCourner.z = bBoxList[2][0]
        

        maxCourner.x = bBoxList[0][1]
        maxCourner.y = bBoxList[1][1]
        maxCourner.z = bBoxList[2][1]

        # Creating the bounding box
        boundingBox = om.MBoundingBox(minCourner, maxCourner)

        return boundingBox
        

    def getObjCenter(self):
        boundingBox = self.getGeoBoundingBox()
        centerPoint =[boundingBox.center().x, boundingBox.center().y, boundingBox.center().z]
        return centerPoint

    def getObjHeight(self):
        boundingBox = self.getGeoBoundingBox()
        return boundingBox.height()

    def getObjDepth(self):
        boundingBox = self.getGeoBoundingBox()
        return boundingBox.height()

    def getObjWidth(self):
        boundingBox = self.getGeoBoundingBox()
        return boundingBox.width()

        
    def __init__(self, rigName, projectEnv):
        
        # IMITIALIZATION
        globalMoveCTL="C_globalMove00_CTL"
        modelGrp = "C_"+rigName+"Model_GRP"
        modelFile = projectEnv+"models/"+rigName+"/"+rigName+".ma"
        # modelFile = projectEnv+"models/"+rigName+"/scenes/s1_v.003.ma"

        mmod.transform.elemIndex = 0

        # COMPONENT FILES
        rigWip, componentsFile, controlShapesFile, skinWeightsFile = folderHierarchy(projectEnv, rigName)

        # NEW SCENE
        mc.file(new = True, f=True)
        
        # IMPORT MODEL
        mc.file(modelFile, i= True, type= "mayaAscii", usingNamespaces= False, f=True)

        # MODEL PARAMETERS
        geoCenter = self.getObjCenter()
        geoHeight = self.getObjHeight()
        geoWidth = self.getObjWidth()
        geoDepth = self.getObjDepth()

        
        # RIG NODE
        mainGrpTransf = mmod.transform(name=rigName, type="GRP") 

        # MODEL GRP
        modelMasterGRP = mmod.transform(name="geometry", type="GRP", parent=mainGrpTransf)
        mc.parent(modelGrp, modelMasterGRP)
        
        # CHARACTER CONTROL SHAPE
        mc.file(controlShapesPath+"/characterControl.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)
        mc.parent(globalMoveCTL, mainGrpTransf)
       
        # CHR CTRL: SCALE & POSITION
        translationVector = [0, geoHeight+geoHeight*0.15, 0]
        fn.scaleShapePoints(globalMoveCTL, geoWidth*0.4)
        fn.translateShapePoints(globalMoveCTL, translationVector, [0, 0, 0])
        
        
        # ROOT CONTROL
        moveGrp = mmod.transform(name="moveGlobal", type="GRP", parent=globalMoveCTL)
        rootCtrl = createJointHY(side= "C", name = "root", parent=moveGrp) 
        # ROOT CTRL: SCALE & POSITION
        fn.scaleShapePoints(rootCtrl[0], max(geoWidth, geoDepth))

        # Create Joint 
        self.rootJnt = mmod.joint(name="root",  parent=rootCtrl)
        # Position JNT: centre of character
        # mc.xform(rootJnt.name, t=geoCenter, ws=True)
        # chrMoveJnt.visibility=0
        # mc.setAttr(jnt.name+".visibility", 0)

        # Other GRP
        self.rigGrp = mmod.transform(name="rig", type="GRP", parent=mainGrpTransf)
        self.jntGRp = mmod.transform(name="jnt", type="GRP", parent=mainGrpTransf)

        # LOAD COMPONENTS
        self.loadLatestFile(componentsFile)



# # MAIN

# # # MAIN
# class roadSig(rigSceneSetup):
#     env = "roadSign"
#     def __init__(self, rigName, projectEnv):
#         super(roadSign, self).__init__(rigName, projectEnv)

# rig = roadSign("s1_GEO", "C:/Users/anama/Desktop/MajorProject/Production/assets/environment")