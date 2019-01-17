import maya.cmds as mc
import functions as fn
import rigFn as rigFn 
import mayaModule as mmod
import mayaNode as mNode


def resetTailMod():
    tail.rigParent = None


    
class tail (object): 
    rigParent=None
    def __init__(self, side="C", tailJnt = None, numbControlPoints=3, name="tail", parent = None, root=None):
        '''
        Tail Types of Controls:
            > Normal FK Controls
            > Global Curl Control
            > Segment Curl Control
        > Switch Between Controls Using a Visibility Switch 
        '''
        # self
        self.side = side
        self.jntGuide = tailJnt
        
        self.parent = parent
        self.root = root
        self.name = name
        self.numbControlPoints = numbControlPoints

        
        # GLOBALS
        mmod.resetJNTCount()
        mmod.resetTRNCount()

        if (parent!=None):
            if (tail.rigParent==None):
                tail.rigParent=mmod.transform(name="tailGlobal", type="GRP", parent=parent.rigGrp)


        if (tailJnt!=None):
            # 1. CREATING THE HIERARCHY
            # FK JNT CHAIN FROM GUIDES
            self.jntGuideList = fn.descendentsList(root=self.jntGuide)
            tailGrp = mmod.transform(side=self.side, name=self.name, type="GRP", parent=self.root)

            # Creating Sec CTL
            self.jntChain = rigFn.createFKChain(self.jntGuideList[1:], side=self.side, name="bind"+self.name.capitalize(), parent=tailGrp)

            # Creating mainControls: mainCtrl, CurCtrl
            offset = len(self.jntChain)/self.numbControlPoints
            mainCtrlParent = mmod.transform(side=self.side, name=self.name+"MainCtrl", type="GRP", parent=tail.rigParent)
            # Parenting main Ctrl to Pelvis
            mc.parentConstraint(self.root, mainCtrlParent.name) 
            # Scaling
            mmod.connectAttr(fn.getParent(self.parent.rootJnt)+".scale", mainCtrlParent.name+".scale")
            curlCtrlParent = mmod.transform(side=self.side, name=self.name+"CurlCtrl", type="GRP", parent=tail.rigParent) 
            mainCtrlList = []
            curlCtrlList = []
            # GLOBAL CURL CTRL
            globalCurlCtrl = rigFn.constructCTL(self.jntGuideList[1], side=self.side, name=self.name+"globalCurlCtrl", parent=curlCtrlParent)
            fn.scaleShapePoints(globalCurlCtrl.name, 1.5)
            # Constraining Global Curl to root
            mc.parentConstraint(self.root.name, globalCurlCtrl.name, mo=True)
            # rigFn.parentConstraint(self.root.name, fn.getParent(globalCurlCtrl.name), globalCurlCtrl.name)
            for i in range (1, len(self.jntChain)-2, offset):
                # MAIN CTRL
                ctrl = rigFn.constructCTL(self.jntGuideList[i], side=self.side, name="control"+self.name, parent=mainCtrlParent)
                fn.scaleShapePoints(ctrl.name, 1.3)
                
                newGrp = mmod.transform(side=self.side, name="bind"+self.name.capitalize(), parent=fn.getParent(self.jntChain[i-1].name), type="GRP")
                mc.parent(self.jntChain[i-1].name, newGrp)

                # Connecting ctrl transfromations to newGrp
                mmod.connectPlugs(ctrl.translate, newGrp.translate)
                mmod.connectPlugs(ctrl.rotate, newGrp.rotate)
                mmod.connectPlugs(ctrl.scale, newGrp.scale)

                mainCtrlList.append(ctrl)
                mainCtrlParent = ctrl

                # CURL CTRL
                curlCtrl = rigFn.constructCTL(self.jntGuideList[i], side=self.side, name="curlCtrl"+self.name, parent=curlCtrlParent)
                # Making curlCtrl follow bindJnt
                # Get NewGrp World Matrix
                decompMatrix = mNode.decomposeMatrix(side=self.side, name=self.name+"BindWM")
                mmod.connectAttr(newGrp.getWorldMatrix(), decompMatrix.getInputMatrix())
                mmod.connectAttr(decompMatrix.getOutputTranslate(), fn.getParent(curlCtrl.name)+".translate")
                mmod.connectAttr(decompMatrix.getOutputRotate(), fn.getParent(curlCtrl.name)+".rotate")
                mmod.connectAttr(decompMatrix.name+".outputScale", fn.getParent(curlCtrl.name)+".scale")
                # Curl Effect
                # Creating add nodes
                if (i>=1):
                    if (i==offset+1):
                        addNode = mNode.plusMinusAverage(side=self.side, name=self.name+"CurlAddition")
                        mmod.connectAttr(globalCurlCtrl.name+".rotate", addNode.name+".input3D[0]")
                        mmod.connectAttr(curlCtrl.name+".rotate", addNode.name+".input3D[1]")
                        addObj = addNode

                    else:
                        addNode = mNode.plusMinusAverage(side=self.side, name=self.name+"CurlAddition")
                        mmod.connectAttr(globalCurlCtrl.name+".rotate", addNode.name+".input3D[0]")
                        mmod.connectAttr(curlCtrl.name+".rotate", addNode.name+".input3D[1]")
                        addObj = addNode
                # Connecting add nodes to jnt Rotation
                for j in range (offset+1):
                    mmod.connectAttr(addNode.getOutput3D(), fn.getParent(self.jntChain[i+j].name)+".rotate")

                    # if (i==1):
                    #     mmod.connectAttr(curlCtrl.name+".rotate", fn.getParent(self.jntChain[i+j].name)+".rotate")

                    # else:

                curlCtrlList.append(curlCtrl)

                fn.scaleShapePoints(curlCtrl.name, 1.3)
                mc.delete(fn.getChildren(curlCtrl)[1])

                

            # Creating Visibility ATTR
            visibility = globalCurlCtrl.addAttr(longName="secondaryCtl", softMinValue=0, defaultValue=0, softMaxValue=1, attrType="short")
            curlCtrlVisibility = globalCurlCtrl.addAttr(longName="curlCtrl", softMinValue=0, defaultValue=1, softMaxValue=1, attrType="short")
            # fkCtrlVisibility = mainCtrlList[0].addAttr(longName="curlCtrl", softMinValue=0, defaultValue=1, softMaxValue=1, attrType="short")
            for jnt in (self.jntChain):
                mmod.connectPlugs(visibility, jnt.visibility)
            # Curl Control Visibility
            for ctrl in curlCtrlList:
                mmod.connectPlugs(curlCtrlVisibility, ctrl.visibility)
            
            # FK Control Visibility
            addition = mNode.addDoubleLinear(side = self.side, name=self.name+"curlSecondaryAdd")
            mmod.connectAttr(globalCurlCtrl.name+".secondaryCtl", addition.getInput1())
            mmod.connectAttr(globalCurlCtrl.name+".curlCtrl", addition.getInput2())
            condition = mNode.condition(side=self.side, name=self.name+"FKControlVisibility")
            condition.operation = 0
            mmod.connectPlugs(addition.output, condition.firstTerm)
            mc.setAttr(condition.getSecondTerm(), 0)
            mc.setAttr(condition.getColorIfFalse(), 0, 0, 0, type = "double3")
            mc.setAttr(condition.getColorIfTrue(), 1, 1, 1, type = "double3")
            mmod.connectAttr(condition.name+".outColorR", mainCtrlList[0].name+".visibility")
                
        # DELETING GUIDES
        mc.delete(tailJnt)

