import maya.cmds as mc
import functions as fn
import rigFn
import mayaModule as mmod
import mNode as mNode



class mouth(object):
    def __init__(self, side="C", name="jaw", jawJnt=None, root=None, parent=None, hook=None):
