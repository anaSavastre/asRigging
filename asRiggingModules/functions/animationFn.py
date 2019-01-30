import maya.cmds as mc

def randomAnimation (animationControls = None, startFrame=0, endFrame=10, frameDencity=3):
    '''
    This is a function designes to create random animation to a set of control objects

    animatonControls = represents the the list of objects the animation will be applied to 
    startFrame = the frame on which the animation will start
    endFrame = last frame of the animation
    frameDensity = this parameter controls how close to one another the frames will be

    '''

    for animControl in animationControls:
        for frame in range (stratFrame, endFrame, frameDensity):
            print frame


randomAnimation("polySphere1", endFrame = 10, frameDencity=1)

