
''' 
Ana Maria Savastre
Bournemouth University 

Major Project: Richest Girl in Town

Prop: Tram


'''

import maya.cmds as mc
import loadFn 
import socket


import maya.OpenMaya as om
import shutil 
import os 
import sys
import mayaModule as mmod
import functions as fn
import pipeline 
import asNodes as asNode
import mayaNode as mNode
import blendFKIK as blendFKIK
import ribbonLimbs as ribbonLimbs



import rigFn as rigFn
import mayaNode as node

import controlFn as ctlFn
if (hostName == "DESKTOP-4NJ3EJ0"):
    projectEnv = "C:/Users/anama/Desktop/MajorProject/Production/MPJ_MASTER/assets/character/"
if (hostName == "DESKTOP-CM0E2QL"):
    projectEnv = "C:/Users/Kari Noriy/Desktop/Ana/asRigging/projects/masterClass/"
if (hostName == "DESKTOP-PQV0HOV"):
    projectEnv = "C:/Users/AnaMaria/Documents/asRigging/projects/masterClass/"

controlShapesPath = "D:/Bournemouth University/asRigging/controlShapes"




class tram(loadFn.rigSceneSetup):    
    character = "Tram"
    def __init__(self, rigName, projectEnv):
        super(tram, self).__init__(rigName, projectEnv)
        
rig=diana("Diana", projectEnv)

