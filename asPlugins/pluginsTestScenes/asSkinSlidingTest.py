import maya.cmds as mc


mc.file(new = True, f=True)


def skinSlidingSetup ():
    polySphere = mc.polySphere(n="C_testSphere00_GEO")
    mc.deformer(type="asSkinSliding")




skinSlidingSetup()