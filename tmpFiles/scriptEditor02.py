import maya.cmds as cmds
import math

def getAnimationData(object, dimension):

    animAttributes = cmds.listAnimatable(object);
    attribute = "|"+object+"."+dimension

    # timeArray = []
    # valueArray = []
     
    if (attribute in animAttributes):
        
        numKeyframes = cmds.keyframe(attribute, query=True, keyframeCount=True)

        if (numKeyframes > 0):
            timeArray = cmds.keyframe(attribute, query=True, index=(0,numKeyframes), timeChange=True)
            valueArray = cmds.keyframe(attribute, query=True, index=(0,numKeyframes), valueChange=True)  
    return timeArray, valueArray

    
def filterCurve(object, endTime=120, filter="simplify", kernel="", maxTimeStep=0.1, minTimeStep=0.1, period=0.1, startTime=0.1, timeTolerance=0.05, tolerance=0.1):
    '''
    endTime = end time of the selection filter
    filter = {"euler", "simplify", "resample"}

    '''
    mc.filterCurve(object, filter=filter, timeTolerance=timeTolerance)

def lineEquation(point1, point2):
    '''
    Returns coefficients a, b, c of equation:
    ax +by +c =0 
    '''
    b = point2[0] - point1[0]
    a = point1[1] - point2[1]
    c = point1[0]*point2[1] - point2[0]*point1[1]

    return a, b, c


def linePointDistance (line, point):
    return abs((line[0]*point[0] +line[1]*point[1]+line[2]))/math.sqrt(line[0]*line[0]+line[1]*line[1])

def findInbetween(timeArray, valueArray, start, end):
    maxDist = 0
    maxDistFrame = 0
    line = lineEquation(start, end )
    for i, (frame, value) in enumerate(zip(timeArray, valueArray)):
        dist = linePointDistance(line, [frame, value])
        if (dist> maxDist):      
            maxDist = dist
            maxDistFrame = i
    return maxDistFrame

def customFiltering(object, dimension):
    attribute = "|"+object+"."+dimension
    timeArray, valueArray = getAnimationData(object, dimension)
    
    # FOR VISUALIZATION
    # KEEP START AND END
    mc.cutKey(attribute, t=(timeArray[1],timeArray[-2]))
    # ITTERATION 1
    for i in range (10):
        # GETTING CURRENT FRAMES
        currentTimeArray, currentValueArray = getAnimationData(object, dimension)
        print "currentTime", currentTimeArray
        for index in range (len(currentTimeArray)-1): 
            # print currentTimeArray[index+1], "next frame"
            start = int(currentTimeArray[index])-1
            end = int(currentTimeArray[index+1])
            print timeArray[start:end], "strat end time"

            
            inbetweenFrame = findInbetween(timeArray[start:end], valueArray[start:end], [currentTimeArray[index], currentValueArray[index]], [currentTimeArray[index+1], currentValueArray[index+1]])
            print "inbetween", inbetweenFrame + start
            frame = mc.setKeyframe(object+"."+dimension, value = valueArray[start + inbetweenFrame], time=timeArray[start + inbetweenFrame])
  

def simplifyAnimation(object):
    animAttributes = cmds.listAnimatable(object)
    for attribute in animAttributes:

        filterCurve(attribute)


# getAnimationData("testObject", "translateZ")

# simplifyAnimation("testObject")

customFiltering("testObject", "rotateZ")
