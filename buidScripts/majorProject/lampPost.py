import maya.cmds as mc
import majorProjectCharacter as mjChr 
import loadFn
import socket


hostName = socket.gethostname()


if (hostName == "DESKTOP-4NJ3EJ0"):
    projectEnv = "C:/Users/anama/Desktop/MajorProject/Production/MPJ_MASTER/assets/character/"


class lampPost(mjChr.rigSceneSetup):    
    character = "lampPost"
    def __init__(self, rigName, projectEnv):
        super(lampPost, self).__init__(rigName, projectEnv)