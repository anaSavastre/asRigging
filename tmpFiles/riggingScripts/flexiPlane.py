''' In this source code I will start by creating the simple structure of an AUTO RIG TOOL''' 

import maya.cmds as cmds
import pymel.core as pm

#clearing the scene
cmds.select(all=True)
cmds.delete()


##########################    Functions    ##########################

def concat_str (str1, str2, s1_begin, s1_end, s2_begin, s2_end):
    
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

def gen_folicles(flc_grpName, flc_name):
    
    '''
     This function is used to create folicles attached on the plane on each of the patches
    in the U direction
    
     '''
    
    #folicle group
    flc_grp=cmds.group (n=flc_grpName, empty=True)
    
    #create a folicle for each of the U patches
    for index in range (0, p_u):
        
        #distance in u between folicles is 1 divided by the number of patches
        dist=1.0/p_u
        
        
        folicle = cmds.createNode('transform', n=flc_name, ss=True)
        folShape = cmds.createNode('follicle', n=flc_name+'Shape', p=folicle, ss=True)
            
        cmds.connectAttr (p_plane[0]+'.local',  folShape+'.inputSurface', f=True);
        cmds.connectAttr (p_plane[0]+'.worldMatrix[0]',  folShape+'.inputWorldMatrix', f=True);
        cmds.connectAttr (folShape+'.outRotate', folicle+'.rotate', f=True)
        cmds.connectAttr (folShape+'.outTranslate', folicle+'.translate', f=True)
    
        cmds.setAttr(folShape+'.parameterU', 0.1+index*dist);
        cmds.setAttr(folShape+'.parameterV', 0.5);
        
        cmds.parent(folicle, flc_grp)
        
    return flc_grp

def gen_nurbsPlane(p_name, p_p, p_ax, p_cH, p_d, p_w, p_lr, p_u, p_v, p_shader, p_colour, p_transparency):
    ''' This function creates the nurbs plane that is used for the flexiSystem 
    It takes in all the parameters needed and creates the plane and assigns a shader to it '''
    
    #create plane command 
    p_plane=cmds.nurbsPlane(n=p_name,p= p_p, ax=p_ax, ch=p_cH, w=p_w, lr=p_lr,d=p_d, u=p_u, v=p_v);
    
    #delete history
    cmds.DeleteHistory(p_plane)
    
    #assign a semitransparent material
    p_material=cmds.shadingNode('lambert', asShader=True, name=concat_str(p_name, 'mtl_01', 0, 2, 0, 0))
    
    #setting attribute materials 
    #colour
    cmds.setAttr(p_material+".color", p_colour[0], p_colour[1],p_colour[2], type='double3')
    #transparency
    cmds.setAttr(p_material+".transparency",  p_transparency[0], p_transparency[1],p_transparency[2], type='double3')
    
    #assigning material to obj
    cmds.select(p_plane[0])
    cmds.hyperShade(  assign=p_material )
    
    return p_plane

def square_cotroller(cv_name):
    points=[(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)]
    cuv_obj=cmds.curve(name=cv_name, p=points, d=1)
    return cuv_obj
    
def felxiPlane_controllers(ctrl_start_name, ctrl_end_name):
    #creating the controllers
    ctrl_start=square_cotroller(ctrl_start_name)
    ctrl_end=square_cotroller(ctrl_end_name)
    #scaling then by 0.6
    cmds.xform(ctrl_start, ctrl_end, s=[ctrl_scale, ctrl_scale, ctrl_scale])
    #translating ctrl to the ends of plane
    cmds.xform(ctrl_start, t=[-5, 0, 0]); cmds.xform(ctrl_end, t=[5, 0, 0])

       

##########################    MAIN    ##########################


#.........................    nurbsPlane: geometry parameters    .........................

#name
p_name='flexiPlane_surface_01';
#pivot    #axis    #construction history    #degree of resulting surface
p_p=[0, 0, 0]; p_ax = [0, 1, 0]; p_cH =1; p_d= 3;
#width
p_w=10;
#length ratio
p_lr=0.2;
#u patches
p_u=5;
#v patches
p_v=1;


#.........................    nurbsPlane: material parameters    .........................

p_shader ='lambert' ; p_colour = [0.0998, 0, 0.118]; p_transparency=[0.6, 0.6, 0.6]

#.........................    folicles: names    .........................
flc_grpName='flexiPlane_grp_flcs_01'
flc_name='flexiPlane_flc_1'

#.........................    controllers: names, parameters    .........................
ctrl_start_name='flexiPlane_ctrl_start_01'
ctrl_end_name='flexiPlane_ctrl_end_01'

ctrl_scale=0.6


# 1. creating the nurbsPlane

p_plane=gen_nurbsPlane(p_name, p_p, p_ax, p_cH, p_d, p_w, p_lr, p_u, p_v, p_shader, p_colour, p_transparency)

# 2. creating the folicles

flc_grp=gen_folicles(flc_grpName, flc_name)

# 3. creating start and end controller

felxiPlane_controllers(ctrl_start_name, ctrl_end_name)


