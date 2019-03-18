import maya.cmds as mc
import os
import functions as fn


def searchAndReplaceText(filePath, searchText="student", repalceText=""):
    with open(filePath,"r+") as file:
        fileData = file.read()
        fileData = fileData.replace(searchText, repalceText)
        file.seek(0)
        file.write(fileData)
        file.truncate()

def nameObj(side="C", name="name"):
    ''' 
    Naming selected objects accordingly
    '''

    selectionList = mc.ls(sl=True)
    # print selectionList
    for i, elem in enumerate(selectionList):
        # Get obj Type
        objType = mc.nodeType(elem, api=True)
        print objType
        # Definig Object Type
        if objType == "kJoint":
            type = "JNT"
        elif objType == "kMesh":
            type = "PLY"
        else:
            type = "TRN"

        mc.rename(elem, side+"_"+name+"0"+str(i)+"_"+type)

def getSceneNamePath():
    '''
    Returns the name of the current scene
    '''
    # Scene name
    fileName = mc.file(q=True, sn=True, shn=True)
    sceneName, extension =  os.path.splitext(fileName)
    return sceneName
def getDirectoryPath():
    projectPath = getScenePath()
    sceneName = getSceneNamePath()
    return projectPath.replace(sceneName+".ma", "")

def getScenePath():
    pathName =mc.file(q=True, sn=True)
    return pathName


# def get
def incrementSave(sceneStrName, versionName, projectPath):
    newVersion =str(int(versionName)+1)

    versionName =  fn.concat_str(str1=versionName, str2=newVersion, s1_begin=0, s1_end=len(newVersion), s2_begin=0, s2_end=0) 
    # versionName.replace(currentVersion,newVersion)
    newName= sceneStrName+versionName

    # Save
    # mc.workspace(dir = projectPath)
    # print projectPath+newName
    mc.file(rn = projectPath+newName+".ma")
    mc.file(save=True, f=True)
    return newName

def saveFile(projectEnv="C:/Users/anama/Desktop/MajorProject/Production", saveName = "newScene"):
    ''' 
    This  function is used to incremently save the current scene and delete the "student" licence from the ma file

    Cases:
        Project is defined:
            function will just increment the current scene
        Project not defined:
        Untitles scene:
            save scene in projectEnv, with name saveName
    '''
    # GLOBALS
    defaultWorkspace="C:/Users/anama/Documents/maya/projects/default/"
    incrementSaveCheck = ".00"
    # saveName = ""

    # Scene name
    sceneName= getSceneNamePath()
    projectPath = getDirectoryPath()
    
    
    if sceneName==None:
        mc.file(rn=projectEnv+"/"+saveName+".0000.ma")
        mc.file(save=True, f=True)

    elif incrementSaveCheck in sceneName:    
        # Check if "000*" in sceneName  
        sceneStrName = fn.concat_str(str1=sceneName, str2="", s1_begin=0, s1_end=4, s2_begin=0, s2_end=0) 
        versionName = fn.concat_str(str1=sceneName, str2="", s1_begin=len(sceneName)-4, s1_end=0, s2_begin=0, s2_end=0) 
        # print versionName
        newScene = incrementSave(sceneStrName, versionName, projectPath)
        
        # get new scene path
        pathName = getScenePath()

        # Clean-up saved file
        # fn.cleanFile (pathName)
        searchAndReplaceText(pathName)

    else:
        # if scene not incremented save, make instance 0000
        mc.file(rn=sceneName+".0000")
        newScene = incrementSave(sceneName, "0000", projectPath)
         # get new scene path
        pathName = getScenePath()

        # Clean-up saved file
        # fn.cleanFile (pathName)
        searchAndReplaceText(pathName)


#ameObj(side="C", name="pillar")