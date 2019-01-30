import maya.cmds as mc
import random as rand

def randomAnimation (animationControls = None, startFrame=0, endFrame=10, frameDensity=3):
    '''
    This is a function designes to create random animation to a set of control objects

    animatonControls = represents the the list of objects the animation will be applied to 
    startFrame = the frame on which the animation will start
    endFrame = last frame of the animation
    frameDensity = this parameter controls how close to one another the frames will be

    '''

    for animControl in animationControls:
        for frame in range (startFrame, endFrame+1, frameDensity):
            currentTranslation = mc.xform(animControl, q=True, ws=True, t=True)
            currentTranslation[0] += rand.random()*(1-frame%2)*frame/2
            currentTranslation[1] += rand.random()*(1-frame%2)*frame/2
            currentTranslation[2] += rand.random()*(1-frame%2)*frame/2
            currentRotation = mc.xform(animControl, q=True, ws=True, ro=True)
            currentRotation[0] += rand.random()*(1-frame%2)*frame/2
            currentRotation[1] += rand.random()*(1-frame%2)*frame/2
            currentRotation[2] += rand.random()*(1-frame%2)*frame/2
            print frame%2
            mc.xform(animControl, t=currentTranslation, ro=currentRotation, ws=True)
            mc.setKeyframe(animControl, time=frame)
            

randomAnimation(["pSphere1"], endFrame = 100, frameDensity=1)

