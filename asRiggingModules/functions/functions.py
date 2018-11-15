import maya.cmds as mc
import os
import sys
import fileinput
# import maya.openMaya as om

##########################    Functions    ##########################


def deleting_pointConstraint(obj):
    ''' This function delets the point constraint from the given obj'''
    #get children
    objChildren=mc.listRelatives(obj, c=True)
    #delete parentConstraint
    for child in objChildren:
        if "pointConstraint" in child:
            mc.delete(child)
def deleting_orientConstraint(obj):
    ''' This function delets the orient constraint from the given obj'''
    #get children
    objChildren=mc.listRelatives(obj, c=True)
    #delete parentConstraint
    for child in objChildren:
        if "orientConstraint" in child:
            mc.delete(child)

def alignTool ():
    ''' This function reads the current selection and aligns the last selected 
    objs to the other two objects '''
    #assigning all selected obj to ctrlString
    objString = mc.ls(sl=True)
    
    #checking if there are any objects selected
    if (len(objString)!=3):
        mc.warning("Current selection not 3! Function can not be performed!")
    else:        
        #point constraint for matching position
        mc.pointConstraint(objString[0], objString[1], objString[2])
        #orient constraint for orientation
        mc.orientConstraint(objString[0], objString[1], objString[2])
        #deleting pointConstrint
        deleting_pointConstraint(objString[2])
        #deleting orientCnstraint
        deleting_orientConstraint(objString[2])

def snapTool(targetObj, obj):
    '''
    Matching of targetObj to the given obj
    
    '''

    #point constraint for matching position
    mc.pointConstraint(targetObj, obj)
    #deleting pointConstrint
    deleting_pointConstraint(obj)

def align(targetObj, obj):
    '''
    Matching orientation and position of targetObj to the given obj
    
    '''

    #point constraint for matching position
    mc.pointConstraint(targetObj, obj)
    #orient constraint for orientation
    mc.orientConstraint(targetObj, obj)
    #deleting pointConstrint
    deleting_pointConstraint(obj)
    #deleting orientCnstraint
    deleting_orientConstraint(obj)



def getSceneName():
    '''
    Returns the name of the current scene
    '''
    # Scene name
    fileName = mc.file(q=True, sn=True, shn=True)
    sceneName, extension =  os.path.splitext(fileName)
    return sceneName

def concat_str (str1="", str2="", s1_begin=0, s1_end=0, s2_begin=0, s2_end=0):
    
    '''.............    TO RECOMMENT     .....................
     This is a function that adds to string strF all the characters form string str from position begin to the end of the string
    
    example:     strF='string' 
                 str ='the example '        => the function will return: strF = 'string example'
                 begin = 3
                 
    '''
    
    string=''
    
    for index in range (s1_begin, len(str1)-s1_end):
        string+=str1[index]
    for index in range (s2_begin, len(str2)-s2_end):
        string+=str2[index]
    
    return string

# def cleanFolder(folderPath):
#     ''' Not working properly'''
#     fileList = os.listdir(folderPath)
#     for file in fileList:
#         file=folderPath+"/"+file
#         print file
#         if os.path.isdir(file):
#             continue
#         else:
#             cleanFile(file, searchText="student", replaceText="")

def cleanFile (filePath, searchText="student", replaceText=""):

    
    tempFile = open( filePath, 'r+' )
    # print "cleanFile"
    
    for i, line in enumerate(fileinput.input(filePath)):
        # print i
        # if searchText in line :
        #     print('Match Found')
        # # else:
            # print('Match Not Found!!')
        tempFile.write( line.replace( searchText, replaceText ) )
    tempFile.close()

def planeEquation(p1, p2, p3):
    ''' 
    ax + by + cz + d = 0

    a = (y2z3 - y3z2) + (y3z1 - y1z3) + (y1z2 - y2z1)
    b = (z2x3 - z3x2) + (z3x1 - z1x3) + ()
    
    '''

    a = (p2[1]*p3[2] - p3[1]*p2[2]) + (p3[1]*p1[2] - p1[1]*p3[2]) + (p1[1]*p2[2] - p2[1]*p1[2])
    b = (p2[2]*p3[0] - p3[2]*p2[0]) + (p3[2]*p1[0] - p1[2]*p3[0]) + (p1[2]*p2[0] - p2[2]*p1[0])
    c = (p2[2]*p3[1] - p3[0]*p2[1]) + (p3[0]*p1[1] - p1[0]*p3[1]) + (p1[0]*p2[1] - p2[0]*p1[1])
    d = -a*p1[0] - b*p1[1] - c*p1[2]
    return [a, b, c, d]


def getChildren(grp):
    '''
    Returns children of given transform node in the outliner 
    '''
    return mc.listRelatives(grp, c=True)
def getParent(grp):
    '''
    Returns parent of given transform node in the outliner 
    '''
    return mc.listRelatives(grp, p=True)[0]

def translateShapePoints(shape, translationVector, pivot):
    shapeList= getChildren(shape)
    # for shape in shapeList:
    # mc.select(shape+"*.cv[0:*]")
    mc.xform(shape+"*.cv[0:*]", t=translationVector, r=True)

def scaleShapePoints(shape, scaleAmount):
    # !!!!!!!!!!!!!! UPDATE FUNCTION: to scale locally not according to world center !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    mc.xform(shape+"*.cv[0:*]", s=[scaleAmount, scaleAmount, scaleAmount], r=True)

def rotateShapePoints(shape, rotationVector=[0, 0, 0], pivot=[0, 0, 0]):

    mc.xform(shape+".cv[0:*]", ro=rotationVector, rp = pivot, os=True)


def descendentsList(root=None):
    descendentsList = mc.listRelatives(root, ad=True)
    descendentsList.append(root)
    descendentsList.reverse()
    
    return descendentsList

