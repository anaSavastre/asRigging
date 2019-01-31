
''' 
Ana Maria Savastre
Bournemouth University 

Master Class Assignment: Frontier Rigging 

Character: Spinosaurus


'''


import maya.cmds as mc
import loadFn 
import socket



# TEMP
import mayaModule as mmod
import functions as fn
import mayaNode as mNode
import rigFn as rigFn 
import mayaNode as node
import asNodes as asNode
import controlFn as ctlFn
import blendFKIK as blendFKIK
import ribbonLimbs as ribbonLimbs


# GLOBALS
hostName = socket.gethostname()

if (hostName == "DESKTOP-4NJ3EJ0"):
    projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-CM0E2QL"):
    projectEnv = "C:/Users/Kari Noriy/Desktop/Ana/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-PQV0HOV"):
    projectEnv = "C:/Users/AnaMaria/Documents/asRigging/projects/masterClass/"



class faceRigSceneSetup (loadFn.rigSceneSetup):
    def __init__(self, rigName, projectEnv):
            
        # INITIALIZATION
        bodyRigFile = projectEnv+"rigging/" +rigName+ "/RIG"
        # NEW SCENE
        mc.file(new = True, f=True)
        # LOAD BODY RIG
        self.loadLatestFile(bodyRigFile)
        print bodyRigFile
        # mc.file (bodyRigFile, i=True, type= "mayaAscii", usingNamespaces= False, f=True)

class spinosaurusFace(faceRigSceneSetup):
    def __init__(self, rigName, projectEnv):
        super(spinosaurusFace, self).__init__(rigName, projectEnv)


spinosaurusFace = spinosaurusFace("Spinosaurus", projectEnv)