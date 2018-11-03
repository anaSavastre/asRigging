import maya.cmds as mc

import shutil 
import os 
import sys
import mayaModule as mmod
import functions as fn
import loadFn 

# GLOBALS
projectEnv = "D:/Bournemouth University/asRigging/projects/masterClass/"
        

class spinosaurus(loadFn.rigSceneSetup):
    character = "lsla"
    def __init__(self, rigName, projectEnv):
        super(spinosaurus, self).__init__(rigName, projectEnv)







rig=spinosaurus("Spinosaurus", projectEnv)
