#Antonio Minondo, Keith Kinnard


import sys
import pygame
import os
from pygame.locals import *

#--------------------------------------------------------------------------------
#********************************PADDLE******************************************
#--------------------------------------------------------------------------------   
     
class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.img = pygame.image.load("images/player1.png")
        w, h = self.img.get_size()
        self.img = pygame.transform.scale(self.img, (int(1*w),int(.5*h)))
        self.rect = self.img.get_rect()
        self.rect.center = (50,240)
        
    '''gets center of object'''
    def get_center(self):
        x = self.rect.centerx
        y = self.rect.centery
        return x, y

    '''move y of center by my'''
    def moveY(self, my):
        self.rect.centery+=my
    
    def setX(self, x):
        self.rect.centerx = x
    
    def setY(self, y):
        self.rect.centery = y
