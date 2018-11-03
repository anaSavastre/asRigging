
def resetCTRL(obj):
    cmds.xform(obj,  os=True, ro=[0, 0, 0], t=[0, 0, 0])


def reset():
    
    objString = cmds.ls(sl=True)
    
    for obj in objString:
        resetCTRL(obj)
        
        
reset()