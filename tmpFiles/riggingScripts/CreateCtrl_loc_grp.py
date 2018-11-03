''' This program creates a hierarchy starting from a joint, it creates a circle controller to which the joint gets parented, then the controller ins 
perented to a locator the cript creates. Next we create a group to which we parent the locator and the hierarchy underneeth it
'''

def concat_str (strF, str, begin):
    
    ''' This is a function that adds to string strF all the characters form string str from position begin to the end of the string
    
    example:     strF='string' 
                 str ='the example '        => the function will return: strF = 'string example'
                 begin = 3
                 
    '''
    
    for index in range (begin, len(str)):
        strF+=str[index]
    return strF
def snapObj(target, obj):
    constr=cmds.pointConstraint(target, obj)
    cmds.delete(constr)

def createHy_for_obj(jntObj):
    
    #variable needed for String Concatenation    
    concatPrefix=4   
    ctrlObj=cmds.circle(n=concat_str('anim', jntObj, concatPrefix))
    
    #placing ctrlObj in the same point as the joint
    snapObj(jntObj, ctrlObj[0])
    
    #freezing transformation and deleting history 
    cmds.makeIdentity(ctrlObj[0], apply=True, t=1, r=1, s=1, n=0, pn=1)
    cmds.DeleteHistory(ctrlObj[0])
    
    #creating locator
    locObj=cmds.spaceLocator(n=concat_str('loc', jntObj, concatPrefix))
    
    #placing ctrlObj in the same point as the joint
    snapObj(jntObj, locObj)
    
    #creating group
    grp=cmds.group(em=True, n=concat_str('grp', jntObj, concatPrefix))
    
    #placing ctrlObj in the same point as the joint
    snapObj(jntObj, grp)
    
    #creating the hierarchy 
    cmds.parent(jntObj,ctrlObj[0])
    cmds.parent(ctrlObj[0], locObj)
    cmds.parent(locObj, grp)

def createHy_main():
    objString = cmds.ls(sl=True)
    for obj in objString:
        createHy_for_obj(obj)
