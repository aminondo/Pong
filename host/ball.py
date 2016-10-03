#Antonio Minondo, Keith Kinnard


import sys
import pygame
import os
from pygame.locals import *
import math
import random 
#--------------------------------------------------------------------------------
#********************************BALL********************************************
#--------------------------------------------------------------------------------   
           
class Ball(pygame.sprite.Sprite):
    def __init__(self):
         pygame.sprite.Sprite.__init__(self)
         self.img = pygame.image.load("images/ball.png")
         self.rect = self.img.get_rect()
         self.rect.center = (320,20)
         self.direction = None
         self.ang = None
         self.win = False
    def moveX(self, mx):
        self.rect.centerx+=mx
    def moveY(self, my):
        self.rect.centery+=my
    def start(self):
        var = random.random()
        print var
        if(self.direction== None and var<.5):
            print "right"
            self.direction = -1
            self.ang = math.pi/4

        if(self.direction== None and var>=.5):
            print "left"
            self.direction = 1
            self.ang = -math.pi/4
    
    '''gets center of object'''
    def get_center(self):
        x = self.rect.centerx
        y = self.rect.centery
        return x, y
    
    def setX(self, x):
        self.rect.centerx = x
    
    def setY(self, y):
        self.rect.centery = y
 