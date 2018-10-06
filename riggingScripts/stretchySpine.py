''' Script for creating stretchy spine skeleton by selecting root joint of the chain '''

import maya.cmds as cmds


def concat_str (strF, str, begin):
    
    ''' This is a function that adds to string strF all the characters form string str from position begin to the end of the string
    
    example:     strF='string' 
                 str ='the example '        => the function will return: strF = 'string example'
                 begin = 3
                 
    '''
    
    for index in range (begin, len(str)):
        strF+=str[index]
    return strF

def createStretchySpine_for_obj (jnt):
    
    ''' This function creates a spline IK handle for a joint. 
    The steps followed:

        #   finding the end joint of the chain in order to call the .ikHandle comand
        #   creating the IK handle
        #   creating cluster deformer for each cv on the curve storing them all in a list 
        #   creating animation controlles for the start and the end of the curve and 
                positioning each ctrl to the same position as the joint
        #   parenting cluster 0 and 1 to animStart and cluster 3 and 4 to animEnd
        #   parent constraining cluster 2 to animStar and animEnd
        
        
        #   creating the stretchy functionalit:
                This requires :
                    #   connecting the arcLen attribute of the curve in a multiplyDivide node as input1X 
                    #   input2X will be given the initial value of the arcLen attribute
                    #   connecting the result of the divission between the current value of the arcLen attrib to the initial one 
                            done in the multiplyDivide node to the scaleX of each joint in the hierarchy        
    '''
           
    #get children
    jntCh=cmds.listRelatives(jnt, ad=True)
    
    endJnt=jntCh[0]
    obj=cmds.select(jnt, endJnt, tgl=True)
    
    #creating the IK handle and cv curve
    ik=cmds.ikHandle (n=concat_str("IK", jnt, 4), sol="ikSplineSolver", pcv=False, ns= 2);
    
    
    IKcurve=cmds.rename (ikCurve, concat_str("IKcurve", jnt, 4))
    #creating cluster deformer for each cv on the curve
    #storing clusters in a list 
    clsList=[]
    for i in range(0,5):
        clsList.append(cmds.cluster(IKcurve+'.cv['+str(i)+']', n=concat_str("cl", jnt, 4)+"_"+str(i)+"_"))
            
    
    #creating ctrl object
    animStart=cmds.circle(n=concat_str("start", jnt, 4))
    animEnd  =cmds.circle(n=concat_str("end", jnt, 4))
    
    #snapping each ctrl to ita joint location
    constr=cmds.parentConstraint(endJnt,animEnd, mo=False)
    cmds.delete(constr)
    constr=cmds.parentConstraint(jnt,animStart,  mo=False)
    cmds.delete(constr)
    
    #deleting the history on the ctrls and freesing transform
    cmds.makeIdentity(animEnd, a=True)
    cmds.makeIdentity(animStart, a=True)
    
    
    #parenting cluster 0 and 1 to animStart and cluster 3 and 4 to animEnd
    cmds.parent(clsList[0][1], clsList[1][1], animStart)
    cmds.parent(clsList[3][1], clsList[4][1], animEnd)
    
    #parent constraining cluster 2 to animStar and animEnd
    cmds.parentConstraint(animStart,clsList[2][1], mo=True)
    cmds.parentConstraint(animEnd,clsList[2][1], mo=True)
    
    #creating the stretchy functionalit
    cvInfo=cmds.arclen(IKcurve,n="cvInfo"+IKcurve,  ch=True)
    
    #creating the expression for the scale
    cvLen=cmds.arclen(IKcurve)
    md=cmds.shadingNode("multiplyDivide", au=True)
    
    #setting operation to diveide
    cmds.setAttr(md+'.operation', 2)
    
    #connecting the arclen in the input 1X
    cmds.connectAttr(cvInfo+".arcLength", md+".input1X", f=True)
    
    #setting the input 2x to cvLen
    cmds.setAttr(md+'.input2X', cvLen)
    
    #connecting saleX of each joint in the hierarchy to the output1X of the multiply divide node
    
    #setting the scale for the root
    cmds.connectAttr(md+".output.outputX ", jnt+".scale.scaleX", f=True)
     
    #doing it for all joints in jntCh
    for obj in jntCh:
        if (cmds.objectType(obj)=="joint"):
            cmds.connectAttr(md+".output.outputX ", obj+".scale.scaleX", f=True)
 
        
def createStretchySpine_main():
    ''' This function reads all the selected joints and then calls the  createStretchySpine_for_obj () function that creates the IK handle for all the 
    objects in the selection'''

    #getting all the obj selected
    objString = cmds.ls(sl=True)
    #resetting the selection
    cmds.select(cl=True)
   
    for obj in objString:
        #calling the function for all elements in the selection        
        createStretchySpine_for_obj(obj) 
        
        
createStretchySpine_main()       