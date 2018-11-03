#This scrip is suposed to automate the process of creating an FK/IK switch. 

'''
    First we will duplicate all the leg joint chain twice and rename them. The first joint chain will be the ik chain as it has the controlers parented to it already
The second will be the bind joint chain and the thirs will be the FK joint chain 

Then it creates a LOCATOR next to each leg to which we add an ATTRIBUTE named "FK_IK_switch". The purpose of the attribute is to control
when the bind joints are manipulated by in an FK/IK way

Next the program applies an orientConstraint between  the FK/IK joints and the bind chain. So that the bind chain can be manipulated by 
either of the two. Therefore, the last procedure needed is setting a key that will alternate the weights of the two constrains. 


                                                        weight of FK chain =1
Which means that: IF:  SWITCH  =  0    =>                                      =>     BIND chain controled by FK


                                                        weight of IK chain =0 
                                                        
                                                        
                                                        weight of FK chain =0
                       SWITCH  =  0    =>                                      =>     BIND chain controled by IK


                                                        weight of IK chain =1 

'''

import maya.cmds as cmds

#.......................................................................................................    FUNCTION DEF    .............................................................................................................................................        




def concat_str (strF, str, begin):
    
    ''' This is a function that adds to string strF all the characters form string str from position begin to the end of the string
    
    example:     strF='string' 
                 str ='the example '        => the function will return: strF = 'string example'
                 begin = 3
                 
    '''
    
    for index in range (begin, len(str)):
        strF+=str[index]
    return strF

def renameDescendents(joints):
    
    ''' This function renames all the descendents of the current joint to have the same prefix as their parent.
    
    IMPORTANT: 
        At this stade the children of "joints" have the same name as the childrem from the 
    chain that we duplicated. Therefore, the function needs to specify the path of the joint when it has to rename it
    The path will be ofcourse the name hold in the "joints" variable + '|' + all parent joints of the current child
    
    PROCEDURE:
        First:     create a list of all the children on the input joint and a "path" variable that initially holds the root joint's name
        Second:    Descendent for loor ( cmds.listRelatives() function returns the children in a list in which the first element is the 
                    last in the  hierarchy, therefore the last element is highest in the chain ) so that we add elements to the path
                    variable in the wright hierarchical order. 
                    Inside the loop the function creates a string that holds the name to assign to the current joint 
                        basically it replaces the "bind_" or "end_" prefix to "IK_" or "FK_"
                        then renames the joint
    
    input variable:
        joints     =     represents the root joint
    
    '''
    
    
    descendentsList= cmds.listRelatives(joints, ad=True)
    path=joints+'|'
    for index in range (len(descendentsList)-1,-1, -1):
       
        elem=descendentsList[index]
                 
        #taking 3 cases for the 3 element types in the hierarchy, 
        #the bind_* joints which will be renamed to IK_*, the end_ which will become end_IK*, and the effector will not be touches (continue)
        current_string=''
        begin= 5#the begin position from which we will start the string
        if ("end_" in elem):
            #end joint case 
            begin=4
            #initialising the current_string to hold the prefix: "end_FK_" or "end_IK_"
            current_string='end_'+joints[0]+joints[1]+'_'  #    joints[0] + joints [1] = "FK" / "IK"
            
        elif ("bind" in elem):
            #bind joint case
            #initialising the current_string to hold the prefix: "bind_FK_" or "bind_IK_"
            current_string+=joints[0]+joints[1]+'_' #    joints[0] + joints [1] = "FK" / "IK"
    
        elif ("effector" in elem):
            #effector case
            continue;
        #adding to the current string the name of the current joint in the hierarchy 
        #(which will be the value of "elem" - the "end" / "bind prefix")
        current_string=concat_str(current_string, elem, begin)
        #renaming just the joints = the elements in the chain that have "01" as sufix
        if (elem[len(elem)-1]=='1'):
            if (elem[len(elem)-2]=='0'):
                cmds.rename(path+elem, current_string)
                path+=current_string+'|' 
          
        
def deleteEffectorBind(joints):
    ''' This function cleans the bind joint chain of all the elemants that are part of the original IK chain (the effector)'''
    descendentsList= cmds.listRelatives(joints, ad=True)
    for elem in descendentsList:
        if ("effector" in elem):
            string="bind*|"+elem
            cmds.delete(string)
            
            
def deleteEffectorFK(joints):
    ''' This function cleans the FK joint chain of all the elemants that are part of the original IK chain (the effector)'''
    descendentsList= cmds.listRelatives(joints, ad=True)
    for elem in descendentsList:
        if ("effector" in elem):
            string="FK*|"+elem
            cmds.delete(string)
   
def deleteConstraintBind(joints):
     ''' This function cleans the bind joint chain of all the elemants that are part of the original IK chain (the constraint)'''
    descendentsList= cmds.listRelatives(joints, ad=True)
    for elem in descendentsList:
        if ("Constraint" in elem):
            string="bind*|"+elem
            cmds.delete(string)
def deleteConstraintFK(joints):
    ''' This function cleans the FK joint chain of all the elemants that are part of the original IK chain (the constraint)'''
    descendentsList= cmds.listRelatives(joints, ad=True)
    for elem in descendentsList:
        if ("Constraint" in elem):
            string="FK*|"+elem
            cmds.delete(string)
            
            
def createSwitchGroup(jointList):
    
    '''
         This function duplicates the IK joint chain that already exists to create a bind and an FK joint chain. 
    To do so it needs to call renameDescendents() funtion that renames an entire joint hierarchy so that each 
    joint chain has the specific prefix (FK/IK/bind) in their name. It then also delets the constraints applied 
    on the IK joint chain
    
    input variable:
        jointList     = list that contains the given joint chains to which we create the IK/FK switch
        
    output variable:
        
        grpNameList   = represents a list will all the FK_IK_switch groups names, needed later on in the program
        
    program variables:
        
        grpN          = a list that will hold the prefix 'FK_IK_switch' and then the name of the first joint in the hierarchy
                        this variable changes in each itteration and is in the end added to the grpNameList
        
        bind_joint    = joint that holds the current joint in from the jointList in the for loop
        IK_joint      = holds the name of the IK root joint in the hierarchy
        FK_joint      = holds the name of the FK root joint in the hierarchy
        
    '''
    
    #switchGrp list with all the switchGrp created in the for loop
    grpNameList=[]
    
    for index in range (0, len(jointList)):
        #creating a name that will hold the name of the final switch group
        grpN='FK_IK_switch'
        begin=4 #to concat the bind prefix (len('bind')=4)
        grpN=concat_str(grpN, jointList[index], begin)
        #adding the curent grp name to the list
        grpNameList.append(grpN)
        
        #bind joint name
        bind_joint=jointList[index]
        
        #creating a string called IK_joint that holds the name of the ik chain
        IK_joint='IK' #initialising the string
        IK_joint=concat_str(IK_joint, jointList[index], begin)
        #now IK_joint should consist of the string : "IK_Hind_l_femur_01" (for the first element in the string)
        #fallowing the same procedure to obtain the FK joint chain
        FK_joint='FK' 
        FK_joint=concat_str(FK_joint, jointList[index], begin)  
        
        #renaming the current joinnt to IK
        cmds.rename(jointList[index], IK_joint)
        #creating the bind joints
        cmds.duplicate(IK_joint, n=bind_joint)
        #renaming all IK its children to have the IK prefix
        renameDescendents(IK_joint)
        #creating the FK joints    
        cmds.duplicate(bind_joint, n=FK_joint)
        #renaming all its children to have the IK prefix
        renameDescendents(FK_joint)
        #deleting the effector and orient Constraint from bind and FK joints hierarchy
        deleteEffectorBind(bind_joint)
        deleteConstraintBind(bind_joint)
        deleteEffectorFK(FK_joint)
        deleteConstraintFK(FK_joint)
        
        #grouping the three sets of joints
        cmds.group(bind_joint, FK_joint, IK_joint,r=True, n=grpN)
    return grpNameList
def createLocator(jointList):
    ''' This function creates a locator for each joint in the list that will hold a custom attribute
    called "FK_IK_switch" that when it is set on 0 it will activate the FK option and when on 1
    it will activate the IK option '''
    
    #creating an empty group that will hold all the switches that will be parented under "Global_01"
    cmds.group(em=True, n="FK_IK_Switches")
    cmds.parent ("FK_IK_Switches", "Global_01")
    
    for index in range (0, len(jointList)):
        begin=5
        #getting the hierarchy list
        hierarchyList=cmds.listRelatives(jointList[index], ad=True)
        locatorName=concat_str ('Switch_',jointList[index] , begin)
        #creating the locator
        cmds.spaceLocator(n=locatorName)
        position=cmds.joint(hierarchyList[1], query=True, a=True)
        #translating the locator -6 units behind each joint
        cmds.xform(locatorName, t=position)
        cmds.xform(locatorName,r=True, t=[0, 0, -6])
        cmds.makeIdentity(locatorName, apply=True, t=1, r=1, s=1, n=0)
        
        #adding the custom attribute "FK_IK_switch" to each locator
        cmds.addAttr(locatorName, ln="FK_IK_switch",k=True, min=0, max=1, dv=0)
        
        #parenting the switch to the "FK_IK_Switches" group
        cmds.parent(locatorName, "FK_IK_Switches")
        
        #orient Constraint the locator to the joint it was placed next to
        cmds.orientConstraint(hierarchyList[1], locatorName, mo=True)
        
        
def orientConstraint_FK_to_bind(bind_root, FK_root):
    
    ''' This function orient constrains all the joints in the bind_root to their equivalent in the FK_root.
    It first creates a list of all the FK joints in the hierarchy and one for the joints in the bind list and then, since the two 
    lists have the same lengths it orientConstrans  bind_list[index] to FK_list[index]'''
    #orient Constraint the hierarchy    
    FK_list=cmds.listRelatives(FK_root, ad=True)
    bind_list=cmds.listRelatives(bind_root, ad=True)
    #orient Constrain the joints in the hierarchy 
    for index in range (len(bind_list)):
        cmds.orientConstraint(FK_list[index], bind_list[index], mo=True)
    #orient Constraint the root joints 
    cmds.orientConstraint(FK_root, bind_root, mo=True)
    
def makeJointList(temp):
    ''' This functiontakes a temporary list that contains a hierarchy and returns a list with all the joints 
    (it excludes the constraints and effectors)'''
    
    final_ls=[]
    #creating the new list that holds just the joints
    for elem in temp:
        if ("effector" in elem):
            continue;
        elif ("Constraint" in elem):
            continue;
        else:
            final_ls.append(elem)
    return final_ls
    
    
        
def orientConstraint_IK_to_bind(bind_root, IK_root):
    
    ''' This function orient constrains all the joints in the bind_root to their equivalent in the IK_root.
    It first creates a list of all the IK joints in the hierarchy and one for the joints in the bind list and then, since the two 
    lists have the same lengths it orientConstrans  bind_list[index] to IK_list[index] '''
    
    #orient Constraint the root joints 
    cmds.orientConstraint(IK_root, bind_root, mo=True)
    
    #orient Constraint the hierarchy    
    IK_list=makeJointList(cmds.listRelatives(IK_root, ad=True))    
    bind_list=makeJointList(cmds.listRelatives(bind_root, ad=True))
    
    for index in range (len(bind_list)):
        cmds.orientConstraint(IK_list[index], bind_list[index], mo=True)
    #orient Constraint the root joints 
    cmds.orientConstraint(IK_root, bind_root, mo=True)    
    
    
def orientConstraintFK_and_IK_to_bing(switchGrp):
    ''' This function takes all switch groups (switchGrp) and parents 
    constraint each joint from the FK and IK hierarchy to their coressponding one from the bind hierarchy
    it calls orientConstraint_FK_to_bind() and orientConstraint_IK_to_bind() that constraint the entire FK and IK chain to the bind chain
    '''
    length=len(switchGrp)
    for index in range (0, length):
        #childrenList holds the bind (childrenList[0]), FK (childrenList[1]) and IK ((childrenList[2])) group root joint for each element in the switchGrp
        childrenList=cmds.listRelatives(switchGrp[index], c=True)
        
        orientConstraint_FK_to_bind(childrenList[0], childrenList[1]) 
        orientConstraint_IK_to_bind(childrenList[0], childrenList[2])

def setDrivKey_for_FK_IK_switch(switchAttr,FKconstraint, IKconstraint):
    #set SWITCH =0, FK weight =1, IK weight =0
    cmds.setAttr(switchAttr, 0)
    cmds.setAttr(FKconstraint, 1)
    cmds.setAttr(IKconstraint, 0)
    #setting key
    cmds.setDrivenKeyframe (FKconstraint, currentDriver=switchAttr)
    cmds.setDrivenKeyframe (IKconstraint,currentDriver=switchAttr)
    #set SWITCH =1, FK weight =0, IK weight =1
    cmds.setAttr(switchAttr, 1)
    cmds.setAttr(FKconstraint, 0)
    cmds.setAttr(IKconstraint, 1)
    #setting key
    cmds.setDrivenKeyframe (FKconstraint, currentDriver=switchAttr)
    cmds.setDrivenKeyframe (IKconstraint,currentDriver=switchAttr)

def createStr_for_DrivKey(switches, jointRoots):
    '''
        This function returns two string one that holds the name of the FK/IK  orientConstraint attribute.
        Input var: jointRoots => holds the name of the joint that is part of the attribute name
        
        returns FKconstraint, IKconstraint which hold the two names
    '''
    
    #particular care for end joint:
    if (jointRoots[0]=="e"):
        FKconstraint=jointRoots+"_orientConstraint1."+concat_str("end_FK_", jointRoots,4)+"W0"
        IKconstraint=jointRoots+"_orientConstraint1."+concat_str("end_IK_", jointRoots,4)+"W1"
    #bind joint case:    
    else:
        FKconstraint=jointRoots+"_orientConstraint*."+concat_str("FK_", jointRoots,5)+"W0"
        IKconstraint=jointRoots+"_orientConstraint*."+concat_str("IK_", jointRoots,5)+"W1"
    return FKconstraint, IKconstraint
        
    


def setDrivKey(jointRoots, switches):
    ''' Last step of the program. It has to key the weight of the orient constraint from the FK/IK joints to bind.
    It calls the functions createStr_for_DrivKey() and setDrivKey_for_FK_IK_switch()
        Performes the setDrivenKey procedure to all the joints in the jointRoot list
    '''
    for index in range (len(jointRoots)):
        #setDrivenKey for root joint
        
        #creating the attribute strings that we will need to use for the set driven key
        switchAttr=switches[index]+".FK_IK_switch"
        FKconstraint, IKconstraint = createStr_for_DrivKey(switches[index], jointRoots[index])
        setDrivKey_for_FK_IK_switch(switchAttr,FKconstraint, IKconstraint)
        
        #doing the same procedure for the entire hierarchy
        bind_list=makeJointList(cmds.listRelatives(jointRoots[index], ad=True))
        for elem in bind_list:
            FKconstraint, IKconstraint = createStr_for_DrivKey(switches[index], elem)
            setDrivKey_for_FK_IK_switch(switchAttr,FKconstraint, IKconstraint)
        
            
            
        
        
    
    
#.......................................................................................................    MAIN CODE    .............................................................................................................................................        
    
#hierarchyList that holds all the leg root joints, the ones we need to duplicate in our first step
leg_root_joints=["bone_r__humerus_02", "bone_l_humerus_02", "bone_r_femur_02", "bone_l_femur_02"]

switchGrpList=createSwitchGroup (leg_root_joints)

#creating the locator, translate it to the 2nd joint from the end and moves it "-6" on Z axis
createLocator(leg_root_joints)


#orient Constraint each joint from the FK and IK hierarchy to their coressponding one from the bind hierarchy
orientConstraintFK_and_IK_to_bing(switchGrpList)

#setting the driven key (when FK_IK_switch =0 => FK activated when FK_IK_switch =1 => IK)
setDrivKey(leg_root_joints,cmds.listRelatives("FK_IK_Switches", c=True))
