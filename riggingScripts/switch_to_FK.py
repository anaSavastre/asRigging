
def setAtrib(attribStr, val):
    cmds.setAttr(attribStr, val)

def cleanCtrlList(descendentsList) :
    ''' This function gets a list of an anim controler hierarchy and returns a list with
    the controlers'''
    #making list just with the controlers
    ctrlList=[]
    for index in range (len(descendentsList)-1,-1, -1):
        if ("Shape" in descendentsList[index] ):
            continue;
        elif ("grp" in descendentsList[index] ):
            continue;
        elif ("Constraint" in descendentsList[index] ):
            continue;
        elif ("jDrv"in descendentsList[index] ):
            continue;
        else :
            ctrlList.append(descendentsList[index])    
    return ctrlList     
      

def GetRotation(jointRoot):
    ''' This function takes the jointRoot variable, generates a list with all its children, and retuns a list with 
    the values of the translation of eache children 
    
    Descendent for loor ( cmds.listRelatives() function returns the children in a list in which the first element is the 
                    last in the  hierarchy, therefore the last element is highest in the chain ) so that we add elements to 
                    the translation list in the right hierarchical order. '''
    
    #declaring the retun list
    rotList=[]
    #finding the descendent list
    descendentsList= cmds.listRelatives(jointRoot, ad=True)
    
    #finding translation of root joint
    rotList.append(cmds.xform(jointRoot, query=True, os=True, ro=True ))
    
    #finding the translation of the descendent joints
    #executing a for from the length to 0 
    
    for index in range (len(descendentsList)-1,-1, -1):
        if (cmds.objectType(descendentsList[index], i="joint")==True):
            rotList.append(cmds.xform(descendentsList[index], query=True, os=True, ro=True ))
            
        
    return rotList
    
def ApplyRot(ctrl, rotList):
    
    ''' This function applies the translation values stored in the rotList to the joints in the hierarchy 
    by rotating the controlers with the valuesf from the rotList'''
    
    #finding the descendent list
    descendentsList= cmds.listRelatives(ctrl, ad=True)
    #cleaning list
    ctrlList=cleanCtrlList(descendentsList)
    #rotating root
    cmds.xform(ctrl, os=True, ro=rotList[0])
    print ctrl, " ", rotList[0]
    
    #rotating the rest of the hierarchy
    for index in range (0, len(ctrlList)):
        cmds.xform(ctrlList[index], os=True, ro=rotList[index+1])
        print ctrlList[index], " ", rotList[index+1]    
    
def match_FK_to_IK (IKjoints, animFK):
    ''' This function stores the values form the GetRotation function in an auxiliary variable 
    rotValList and then calls the ApplyRot function that rotates each controler with the 
    coresponding values from the rotation list variable'''
    #getting the translation values of IKjoints
    rotValList=GetRotation(IKjoints) 
    print rotValList  
    #applying the translation values to the jointApply to FK
    ApplyRot(animFK,rotValList)
        

def match_FK_to_IK_trans (IKjoints, animFK):
    ''' This function stores the values form the GetTranslation function in an auxiliary variable 
    transValList and then calls the ApplyTranslation function that translates each controler with the 
    coresponding values from the translation list variable'''
    
    #getting the translation values of IKjoints
    transValList=GetTranslation(IKjoints)
    print transValList
    #applying the translation values to the jointApply to FK
    ApplyTranslation(animFK,tranValList)
    
def match_IK_to_FK(animFK, animIK):
    ''' This function mathces the position of the IK anim ctrl to the 
    FK_ankle ctrl by point constraining the animIK to the animFK
    and then deleting the constraint 
    '''
    #get last FK ctrl hierarchy 
    descendentsList=cmds.listRelatives(animFK, ad=True)
    
    #cleaning list
    ctrlList=cleanCtrlList(descendentsList)
    #getting the second last last anim
    anim=ctrlList[len(ctrlList)-2]
    
    constr=cmds.pointConstraint(anim, animIK)
    cmds.delete(constr)



def switch_FK_IK(animFK, animIK, switch):
    #creating attribute switch
    attribStr=switch+".FK_IK_switch"
    match_IK_to_FK(animFK, animIK)
    setAtrib(attribStr, 1)


def hind_l_leg_switch():
    switch="Switch_l_femur_01"
    IKjoints="IK_l_femur_01"
    animFK="anim_FK_Hind_l_femur_01"
    animIK="anim_l_IK_hind_leg_01"
    switch_FK_IK(switch, IKjoints, animFK, animIK)
    
    
    
hind_l_leg_switch