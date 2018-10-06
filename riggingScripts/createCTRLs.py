

def ctrl(jnt):
    #creating the group
    name='anim_'+jnt
    ctrl=cmds.circle(n=name)
    grpName='grp'+name
    grp=cmds.group(ctrl, n=grpName)
    
    #positioning the group
    constraint=cmds.pointConstraint(jnt,grp)
    cmds.delete(constraint)
    
    #orienting group
    constraint=cmds.orientConstraint(jnt, grp)
    cmds.delete(constraint)
    
    
    
    #freezeTransformatins on ctrl
    return grp, ctrl

def createCTRL(root):
    descendentsList= cmds.listRelatives(root, ad=True)
    print descendentsList
    p_grp, p_ctrl= ctrl(root)
    #copy p_grp to return
    root_grp=p_grp
    #parenting joint
    cmds.parentConstraint(p_ctrl, root)
    #applying ctrl function to all descendents (elem 0 will be end joint => start loop from elem 1)
    for index in range (len(descendentsList)-1, 0, -1):
        c_grp, c_ctrl=ctrl(descendentsList[index])
        cmds.parent(c_grp, p_ctrl)
        #parenting joint to ctrl
        cmds.parentConstraint(c_ctrl, descendentsList[index])
        
        #resset parents
        p_ctrl=c_ctrl; p_grp=c_grp
        
        
        
    return root_grp
        

def createCTRL_for_list (jntList, ctrlGrp):
    for jntRoot in jntList:
        grp_root=createCTRL(jntRoot)
        #parenting the controlers to contoller grp 
        cmds.parent(grp_root, ctrlGrp)
        
    


#controller grp
ctrlGrp='Controlers'
#hierarchyList that holds all the leg root joints, the ones we need to duplicate in our first step
leg_root_joints=cmds.ls(sl=True)

createCTRL_for_list(leg_root_joints, ctrlGrp)

jnt="FK_l_femur_01"


