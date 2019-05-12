import rigFn as rigFn
import functions as fn
import mayaModule as mmod
import mayaNode as mNode                            
import maya.cmds as mc
                         
rigFn.parentConstraintMO("L_armIKWrist03_CTL", "L_hand00_GRP", "L_handFK_wrist01_GRP", maintainOffset = True, translate=True, rotate=True, scale=True)
 
# BIND                                              JOINTS
bindJoints = [ u'C_chest04_JNT', u'C_bindSpine06_JNT', u'C_bindSpine010_JNT', u'C_bindSpine09_JNT', u'C_bindSpine08_JNT', u'C_bindSpine07_JNT',
                       u'C_pelvis01_JNT', u'L_bindFemurribbon01_JNT', u'L_bindFemurribbon00_JNT',
                       u'L_bindFemurribbon02_JNT', u'L_bindFemurribbon03_JNT', u'L_bindFemurribbon04_JNT',
                        u'L_bindTibiaribbon00_JNT', u'L_bindTibiaribbon01_JNT', u'L_bindTibiaribbon02_JNT', u'L_bindTibiaribbon03_JNT',
                        u'L_bindTibiaribbon04_JNT', u'R_bindFemurribbon00_JNT', u'R_bindFemurribbon01_JNT',
                        u'R_bindFemurribbon02_JNT', u'R_bindFemurribbon03_JNT', u'R_bindFemurribbon04_JNT', 
                        u'R_bindTibiaribbon00_JNT', u'R_bindTibiaribbon01_JNT', u'R_bindTibiaribbon02_JNT', u'R_bindTibiaribbon03_JNT',
                        u'R_bindTibiaribbon04_JNT', u'L_footFK_Ankle00_JNT', u'R_footFK_Ankle00_JNT',
                        u'R_footFK_Tarsals01_JNT', u'L_footFK_Tarsals01_JNT', u'L_bindHumerusribbon01_JNT', u'L_bindHumerusribbon00_JNT',
                        u'L_bindHumerusribbon02_JNT', u'L_bindHumerusribbon03_JNT', u'L_bindHumerusribbon04_JNT',
                        u'L_bindRadiusribbon00_JNT', u'L_bindRadiusribbon01_JNT', u'L_bindRadiusribbon02_JNT', u'L_bindRadiusribbon03_JNT',
                        u'L_bindRadiusribbon04_JNT', u'R_bindHumerusribbon00_JNT', u'R_bindHumerusribbon01_JNT',
                        u'R_bindHumerusribbon02_JNT', u'R_bindHumerusribbon03_JNT', u'R_bindHumerusribbon04_JNT',
                        u'R_bindRadiusribbon00_JNT', u'R_bindRadiusribbon01_JNT', u'R_bindRadiusribbon02_JNT', u'R_bindRadiusribbon03_JNT',
                        u'R_bindRadiusribbon04_JNT', u'L_bindClavicle012_JNT', u'R_bindClavicle012_JNT', 
                        u'L_handFK_wrist00_JNT', u'R_handFK_wrist00_JNT', 
                        u'L_thumbMetacarpal00_JNT', u'L_thumbProximalPhalange02_JNT', u'L_thumbMiddlePhalange04_JNT',
                        u'R_thumbMetacarpal00_JNT', u'R_thumbProximalPhalange02_JNT', u'R_thumbMiddlePhalange04_JNT',
                        u'L_indexMetacarpal00_JNT', u'L_indexProximalPhalange02_JNT', u'L_indexMiddlePhalange04_JNT', 
                        u'L_indexDistalPhalange06_JNT', u'L_middleMetacarpal00_JNT', u'L_middleProximalPhalange02_JNT', 
                        u'L_middleMiddlePhalange04_JNT', u'L_middleDistalPhalange06_JNT', u'L_ringMetacarpal00_JNT', 
                        u'L_ringProximalPhalange02_JNT', u'L_ringMiddlePhalange04_JNT', u'L_ringDistalPhalange06_JNT',
                        u'L_pinkyMetacarpal01_JNT', u'L_pinkyProximalPhalange03_JNT', u'L_pinkyMiddlePhalange05_JNT',
                        u'L_pinkyDistalPhalange07_JNT', u'R_indexMetacarpal00_JNT', u'R_indexProximalPhalange02_JNT',
                        u'R_indexMiddlePhalange04_JNT', u'R_indexDistalPhalange06_JNT', u'R_middleMetacarpal00_JNT',
                        u'R_middleProximalPhalange02_JNT', u'R_middleMiddlePhalange04_JNT', u'R_ringMetacarpal00_JNT', 
                        u'R_pinkyMetacarpal01_JNT', u'R_pinkyProximalPhalange03_JNT', u'R_ringProximalPhalange02_JNT', 
                        u'R_pinkyMiddlePhalange05_JNT', u'R_ringMiddlePhalange04_JNT', u'R_pinkyDistalPhalange07_JNT',
                        u'R_ringDistalPhalange06_JNT', u'R_middleDistalPhalange06_JNT', 
                        u'L_thumbMetacarpal01_JNT', u'L_thumbProximalPhalange03_JNT', u'L_indexMetacarpal01_JNT', 
                        u'L_indexProximalPhalange03_JNT', u'L_indexMiddlePhalange05_JNT', u'L_middleMetacarpal01_JNT',
                        u'L_middleProximalPhalange03_JNT', u'L_middleMiddlePhalange05_JNT', u'L_ringMetacarpal01_JNT', 
                        u'L_ringProximalPhalange03_JNT', u'L_ringMiddlePhalange05_JNT', u'L_pinkyMetacarpal02_JNT', 
                        u'L_pinkyProximalPhalange04_JNT', u'L_pinkyMiddlePhalange06_JNT', 
                        u'R_thumbMetacarpal01_JNT', u'R_thumbProximalPhalange03_JNT', u'R_indexMetacarpal01_JNT', 
                        u'R_indexProximalPhalange03_JNT', u'R_indexMiddlePhalange05_JNT', u'R_middleMetacarpal01_JNT',
                        u'R_middleProximalPhalange03_JNT', u'R_middleMiddlePhalange05_JNT', u'R_ringMetacarpal01_JNT', 
                        u'R_ringProximalPhalange03_JNT', u'R_ringMiddlePhalange05_JNT', u'R_pinkyMetacarpal02_JNT', 
                        u'R_pinkyProximalPhalange04_JNT', u'R_pinkyMiddlePhalange06_JNT', 
                        u'C_bindNeck03_JNT', u'C_bindNeck04_JNT', u'C_bindNeck07_JNT',
                        u'C_bindNeck06_JNT', u'C_bindNeck05_JNT', u'C_head00_JNT']

mc.select(bindJoints, "C_Diana00_GEO")

# mmod.resetJNTCount()

# grp = "C_apperture00_GRP"

# for i, elem in enumerate(fn.getChildren(grp)):
#     # Creating Joint 
#     position = mc.xform(elem+".vtx[47]", ws=True, t=True, q=True)

#     jnt = mmod.joint(name = "appertureBlade")
#     mc.xform(jnt, t=position, ws=True)

#     mc.parentConstraint (jnt, elem, mo=True)

# rigFn.constructCTL("joint1", name="lightApperture")

# Adding close attribute
# mc.addAttr("C_lightApperture01_CTL", longName="apperture", min=0, max = 0.7, at="doubleAngle", k=True)

# for jnt in fn.getChildren("C_appertureBladeJoints00_GRP"):
#     # Connect Attr
#     animBlen = mNode.animBlendNodeAdditiveDA(name="reverseAngle")
#     mmod.connectAttr("C_lightApperture01_CTL.apperture", animBlen.getInputA())
#     animBlen.weightA = -1
#     mmod.connectAttr(animBlen.getOutput(), jnt+".rotateY")


# mc.parentConstraint("C_lightApperture012_JNT", "C_lightBox00_GEO",mo=True)


# import jawModule as jawMod



# mmod.resetCount()
# jawMod.jaw(jawJnt="C_jaw00_JNT", root="C_headBase00_JNT")

# rigFn.constructCTL("C_head00_JNT1", side="C", name="headTop", parent="C_head00_JNT", ctrlScale=1, ctrlShape=0)