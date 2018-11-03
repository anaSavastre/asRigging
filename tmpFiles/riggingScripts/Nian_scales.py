''' 
    This program creates a hierarchy starting from a nHair follicle, it creates a circle controller to which a 
joint gets parented. Then the controller is parented to a locator. Next we create a group to which we parent the
locator and the hierarchy underneath it

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
    ''' Function that snaps an object to a target, by applying a point constraint to it and then deleting it'''
    constr=cmds.pointConstraint(target, obj)
    cmds.delete(constr)

def createHy_for_obj(flcObj):
    
    ''' This is the main'''
    
    print flcObj
    #variable needed for String Concatenation    
    concatPrefix=36
    ctrlObj=cmds.circle(n=concat_str('anim', flcObj, concatPrefix))
    
    #placing ctrlObj in the same point as the joint
    snapObj(flcObj, ctrlObj[0])
    
    #freezing transformation and deleting history 
    cmds.makeIdentity(ctrlObj[0], apply=True, t=1, r=1, s=1, n=0, pn=1)
    cmds.DeleteHistory(ctrlObj[0])
    
    #creating locator
    jntObj=cmds.joint(n=concat_str('bind', flcObj, concatPrefix), rad=0.2)
    
    #placing jntObj in the same point as the folicle
    snapObj(flcObj, jntObj)
    
    
    #creating the hierarchy 
    #cmds.parent(ctrlObj[0], jntObj)
    #parent constraint ctrl to folicle
    cmds.parentConstraint(flcObj, ctrlObj[0], mo=True)
    

def createHy_main():
    objString = cmds.ls(sl=True)
    for obj in objString:
        #scale constraining each flc to root
        cmds.scaleConstraint("root_01", obj)
        createHy_for_obj(obj)

createHy_main()