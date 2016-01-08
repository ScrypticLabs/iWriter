#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Abhi Gupta
# @Date:   2015-06-07 20:22:39
# @Last Modified by:   Abhi Gupta
# @Last Modified time: 2015-06-07 20:25:22
# Plots the Gaze Positions

from math import hypot

def dist(p1, p2):   # declare pararmeters as array
    """Finds the distance between the old and new position"""
    return hypot(p1[0]-p2[0],p1[1]-p2[1])

def normal(x, y):
    """Normalizes the movement"""
    d = hypot(x,y)
    return (x/d,y/d)

def add(v1, v2):
    """adds vectors"""
    v1[0]+=v2[0]
    v1[1]+=v2[1]

def mult(v1, m):
    """multiplies a vector"""
    return (v1[0]*m,v1[1]*m)

def intt(tup):
    """Returns a tuple components as ints"""
    return (int(tup[0]),int(tup[1]))
    
def getPoints(dest, old_dest, circ, speed, maxAccel, maxSpeed):
    """This function is called externally. Finds the accerleration of movement"""
    distance = hypot(dest[0]-old_dest[0], dest[1]-old_dest[1])
    if 15 <= distance <= 45:
        maxSpeed *= distance
        maxAccel *= 1.5
    elif distance >= 46:
        maxSpeed *= distance*2
        maxAccel *= 4
    else:
        maxSpeed = 60
        maxAccel = 100
    d = dist(circ,dest)
    if d > 0:
        direct = normal(dest[0]-circ[0],dest[1]-circ[1])
        speed = min(speed+maxAccel,min(maxSpeed,d))
        add(circ,mult(direct,speed))
    return intt(circ)
