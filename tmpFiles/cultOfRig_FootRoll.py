import maya.cmds as cmds
import mayaModule as mmod




def jointSetUp():
    # Creating grp:
    '''
    C_footRoll_Grp
        >input
        >control
            >configParameters
            >animParam
            >sth
    '''
    footRoll = mmod.transform(name="footRoll", type="GRP")
    input = mmod.transform(name="input", type="GRP", parent=footRoll)
    control = mmod.transform(name="control", type="GRP", parent=footRoll)

    configParameters = mmod.transform(name="configParameters", type="GRP", parent=control)
    animParameters =  mmod.transform(name="animParameters", type="GRP", parent=control)
    guidingParameters =  mmod.transform(name="guidingParameters", type="GRP", parent=control)
    tempJnt = mmod.transform(name="tempJnt", type="GRP", parent=control)

    # AddAttr 
    '''
    roll
    tarsal
    straighten

    '''

    mc.addAttr( animParameters, ln="footRoll", smn=-1.7, smx=3.14, at="doubleAngle", k=True)
    mc.addAttr( animParameters, ln="tarsalLock", smn=-1.7, smx=3.14, at="doubleAngle", k=True)
    mc.addAttr( animParameters, ln="straighten", smn=-1.7, smx=3.14, at="doubleAngle", k=True)

    mc.addAttr(guidingParameters, ln="toeRest", smn=-1.7, smx=3.14, at="doubleAngle", k=True)
    mc.addAttr(guidingParameters, ln="tarsalRest", smn=-1.7, smx=3.14, at="doubleAngle", k=True)
    mc.addAttr(guidingParameters, ln="heelLength", smn=0.01, smx=10, at="double", k=True)
    mc.addAttr(guidingParameters, ln="toeLength", smn=0.01, smx=10, at="double", k=True)
    mc.addAttr(guidingParameters, ln="tarsalLength", smn=0.01, smx=10, at="double", k=True)

    mc.setAttr(guidingParameters.name+".heelLength", -8)
    mc.setAttr(guidingParameters.name+".toeLength", 4)
    mc.setAttr(guidingParameters.name+".tarsalLength", 4)
    mc.setAttr(guidingParameters.name+".tarsalRest", 30)
   

    # Creating joints !!!!!!!!!!!!!!!!!!! Change when doing leg Module
    heelJnt=mmod.joint(name="heel", parent=tempJnt)
    toesJnt = mmod.joint(name="toes", parent=heelJnt)
    tarsalJnt = mmod.joint(name="tarsal", parent=toesJnt)
    ankleJnt = mmod.joint(name="ankle", parent = tarsalJnt)

    # Connecting attr !!!!!!!!!!!!!!!!!!! Change when doing leg Module
    mc.connectAttr(guidingParameters.name+".heelLength", toesJnt.name+".translateX")
    # guidingParameters.toeLength > jnt1.tx
    mc.connectAttr(guidingParameters.name+".toeLength", tarsalJnt.name+".translateX")
    
    # guidingParameters.tarsalLength > jnt2.tx
    mc.connectAttr(guidingParameters.name+".tarsalLength", ankleJnt.name+".translateX")

     # guidingParameters.toeLength > jnt1.tx
    mc.connectAttr(guidingParameters.name+".toeRest", toesJnt.name+".rotateZ")
    
    # guidingParameters.tarsalLength > jnt2.tx
    mc.connectAttr(guidingParameters.name+".tarsalRest", tarsalJnt.name+".rotateZ")

    return [heelJnt, toesJnt, tarsalJnt, ankleJnt], [animParameters, guidingParameters]



def scene():
    mmod.transform.elemIndex = 0
    mmod.joint.elemIndex = 0
    mc.file(new = True, f=True)
    # mc.file("C:/Users/anama/Documents/maya/projects/default/scenes/footrolltest.0002.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)
    mc.file("D:/Bournemouth University/asRigging/tmp/footRoll.ma", i= True, type= "mayaAscii", usingNamespaces= False, f=True)

    # Jnt setUp
    # footJnts, parametersGrps = jointSetUp()
    
    
    # FootRollConnections

    # Connecting to ankle
    cube = mc.polyCube(name="ankle")
    ankleRest = mmod.transform(name="ankleRest", parent="C_footRoll00_GRP")

scene()