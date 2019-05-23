import maya.cmds as mc
import maya.OpenMaya as om
import functions as fn
import rigFn
import mayaModule as mmod
import mayaNode as mNode

'''
Eyelids Module:
 
'''


class eyeLids(object):
    root = None
    parent = None

    def selectCV(self, controlList):
        for ctrl in controlList:
            for shape in fn.getChildren(ctrl)[:-1]:
                mc.select(shape+".cv[*]", tgl=True)

    def createJoint(self, guideObjectsList):
        self.selectCV(guideObjectsList)

        self.selectionBoundingBox = fn.getBoundingBox()
        center = self.selectionBoundingBox.center()

        mc.select(clear=True)
        jnt = mc.joint(p=[center.x, center.y, center.z])
        return jnt

    def __init__(self, side="C", name="eyeLid", eyeLidGuides=None, root=None, parent=None, hook=None):
        '''

        root = direct descendence
        parent = Extras (rigGRP)
        hook = eyeJnt

        '''
        # GLOBALS
        self.side = side
        self.name = name
        if (root != None):
            if (eyeLids.root == None):
                eyeLids.root = mmod.transform(
                    name="eyeLidsRoot", type="GRP", parent=root)

        if (parent != None):
            if (eyeLids.parent == None):
                eyeLids.parent = mmod.transform(
                    name="eyeLidsGlobal", type="GRP", parent=parent)
        self.hook = hook

        self.eyeLidGuide = fn.getChildren(eyeLidGuides)

        mmod.resetCount()

        # Creating Controlls
        # LOCAL CONTROLS
        localControls = mmod.transform(
            side=self.side, name=self.name+"LocalControls", type="GRP", parent=eyeLids.root)
        self.eyeLidsControls = []
        for guide in self.eyeLidGuide:
            self.eyeLidsControls.append(rigFn.constructCTL(
                guide, side=self.side, name=self.name, parent=localControls, ctrlShape=6))
            joint = mmod.joint(side=self.side, name=self.name,
                               parent=fn.getChildren(self.eyeLidsControls[-1])[-1])
            fn.align(fn.getChildren(guide)[0], joint)
            # Transalting ControlShapes
            for shape in fn.getChildren(self.eyeLidsControls[-1])[:-1]:
                if (self.side == "R"):
                    translateX = (mc.getAttr(
                        fn.getChildren(guide)[0]+".translateX")) * -1
                else:
                    translateX = mc.getAttr(
                        fn.getChildren(guide)[0]+".translateX")

                fn.translateShapePoints(shape, [translateX, 0, 0], [0, 0, 0])

        # GLOBAL CONTROL
        # Construct Guide
        # Root
        rootJnt = mmod.joint(side=side, name=self.name+"Guide")
        fn.align(eyeLidGuides, rootJnt)
        # FreezTransforms
        mc.makeIdentity(rootJnt, apply=True, r=True)
        # Child
        childJnt = self.createJoint(self.eyeLidsControls)
        mc.parent(childJnt, rootJnt)
        mc.joint(rootJnt, e=True, oj="xyz", sao="yup", ch=True, zso=True)
        mc.setAttr(childJnt+".jointOrient", 0, 0, 0, type="double3")
        # Construct Control
        globalControl = rigFn.constructCTL(
            rootJnt, side=self.side, name=self.name+"Global", parent=eyeLids.root, ctrlShape=0)

        # Rotate Shape
        fn.rotateShapePoints(globalControl.name, rotationVector=[
                             0, 90, 0], pivot=[0, 0, 0])
        # Scale from Bounding Box Parameters (length and Height)
        fn.vectorScaleShapePoints(globalControl.name, [0, self.selectionBoundingBox.height(
        ) * 0.5, self.selectionBoundingBox.width() * 0.5])
        # fn.scaleShapePoints(globalControl.name, self.selectionBoundingBox.width())
        # fn.vectorScaleShapePoints(globalControl.name, [1, 1, self.selectionBoundingBox.width() * rootJnt.getRadius() ])

        # Transalting ControlShapes
        for shape in fn.getChildren(globalControl)[:-1]:
            fn.translateShapePoints(
                shape, [mc.getAttr(childJnt+".translateX"), 0, 0], [0, 0, 0])

        # COLLISION EYELID
        # For every eyeLid Create Aim Object
        for i, jnt in enumerate(self.eyeLidGuide):
            guide = fn.getChildren(jnt)

            aimObject = mmod.transform(
                side=self.side, name=self.name+"AimObject", type="GRP", parent=guide)
            # Parent to eye joint
            mc.parent(aimObject, self.hook)

        #     # Aim Constraint
        #     # if (self.side == "R"):

        #     #     mc.aimConstraint(aimObject, self.eyeLidsControls[i], aim=[1, 0, 0], u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root, mo=True)

        #     # mc.aimConstraint(aimObject, fn.getParent(self.eyeLidsControls[i]), aim=[1, 0, 0],
        #     #                  u=[0, 1, 0], worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=self.root, mo=True)

        # # CLEAN-UP
        # mc.delete(rootJnt)


def getVectorBetween(startObject, endObject, side="C", name="name"):
    # Decompose Matrix
    matrixStart = mNode.decomposeMatrix(side=side, name=name+"Start")
    matrixEnd = mNode.decomposeMatrix(side=side, name=name+"End")
    plusMin = mNode.plusMinusAverage(side=side, name=name+"Vector")
    plusMin.operation = 2
    try:
        mmod.connectAttr(endObject.getWorldMatrix(),
                         matrixEnd.getInputMatrix())
    except:

        mmod.connectAttr(endObject+".worldMatrix", matrixEnd.getInputMatrix())

    try:
        mmod.connectAttr(startObject.getWorldMatrix(),
                         matrixEnd.getInputMatrix())
    except:

        mmod.connectAttr(startObject+".worldMatrix",
                         matrixEnd.getInputMatrix())

    mmod.connectAttr(matrixEnd.getOutputTranslate(),
                     plusMin.name+".input3D[0]")
    mmod.connectAttr(matrixStart.getOutputTranslate(),
                     plusMin.name+".input3D[1]")

    return plusMin.getOutput3D()


def globalToLocalConnection(globalJointsList=[], localJointsList=[], restGroupParent=None, side="C", name="restEyeLid"):

    for glJnt, locJnt in zip(globalJointsList, localJointsList):
        # CREATE REST OBJECT
        restParent = mmod.transform(
            side=side, name=name, type="GRP", parent=glJnt)
        restChild = mmod.transform(
            side=side, name=name, type="GRP", parent=fn.getChildren(glJnt)[-1])
        # Parenting under RestGroup
        mc.parent(restParent, restGroupParent)
        mc.parent(restChild, restParent)

        # REST VECTOR
        restVect = getVectorBetween(
            restParent, restChild, side=side, name=name+"Rest")

        # ACCTIVE VECTOR
        acctiveVect = getVectorBetween(glJnt, fn.getChildren(
            glJnt)[-1], side=side, name=name+"Acctive")

        # ANGLE BETWEEN
        angle = mNode.angleBetween(side=side, name=name+"Rotation")

        mmod.connectAttr(restVect, angle.getVector1())
        mmod.connectAttr(acctiveVect, angle.getVector2())
        mmod.connectAttr(angle.name+".eulerX", locJnt+".rotateZ")


def createEyeDiana():

    for s in ["L", "R"]:

        m_lids = eyeLids(side=s, name="lowerEyeLids", eyeLidGuides=s+"_lowerEyeLid00_GRP",
                         root="C_headTop00_CTL", parent="C_rig00_GRP", hook=s+"_localEye0*_JNT")

        m_lids = eyeLids(side=s, name="upperEyeLids", eyeLidGuides=s+"_upperEyeLid00_GRP",
                         root="C_headTop00_CTL", parent="C_rig00_GRP", hook=s+"_localEye0*_JNT")


# Connections
globalJnt = [u'L_upperEyeLids00_JNT', u'L_upperEyeLids02_JNT',
             u'L_upperEyeLids04_JNT', u'L_upperEyeLids06_JNT']
localJnt = [u'L_localUpperEyeLid00_JNT', u'L_localUpperEyeLid02_JNT',
            u'L_localUpperEyeLid04_JNT', u'L_localUpperEyeLid06_JNT']
globalToLocalConnection(globalJointsList=globalJnt, localJointsList=localJnt,
                        restGroupParent="C_eyeLidsRest00_GRP", side="L", name="restUpperEyeLid")


# createEyeDiana()
