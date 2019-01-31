import maya.cmds as mc
import os

def getVersion(path):
    files= os.listdir(path)
    increment = len(files)
    if (increment<10):
        version = "000"+str(increment)
    elif (increment>=10 and increment<100):
        version = "00"+str(increment)
    elif (increment>100 and increment<1000):
        version = "0"+str(increment)
    else:
        version = +str(increment)

    return version
    

def getLatestVersion(path):
        '''
        This function gets a path file
        Returns the latest version
        '''
        files= os.listdir(path)
        latestFile = sorted(files)[-1];

        return latestFile

def saveSkinWeight(weightsFile="skinWeights", path="D:/Bournemouth University/asRigging/tmp/tmpSkinWeights", deformer="skinCluster*"):

    # GET ALL DEFORMERS IN SCENE
    deformerList = mc.ls( typ="skinCluster")
    if (projectEnv):
        path = projectEnv+"rigging/Spinosaurus/wip/skinWeights"
        # GET VERSION NUMBER
        version = getVersion(path)

        mc.deformerWeights(weightsFile+version+".xml", path=path, ex=True, deformer=deformerList)

    
    else:
        # GET VERSION NUMBER
        version = getVersion(path)
 
        mc.deformerWeights(weightsFile+version+".xml", path=weightsFile, ex=True, deformer=deformerList)

# saveSkinWeight()
def loadSkinWeights(weightsFile="skinWeights", path="D:/Bournemouth University/asRigging/tmp/tmpSkinWeights", deformer="skinCluster*"):

    if (projectEnv):
        path = projectEnv+"rigging/Spinosaurus/wip/skinWeights"
        # GET FILE
        file = getLatestVersion(path)

        mc.deformerWeights(file, path=path, im=True, deformer=deformer)

    
    else:
        # GET FILE
        file = getLatestVersion(path)

        mc.deformerWeights(file, path=path, im=True, deformer=deformer)


# loadSkinWeights()
#
saveSkinWeight()
