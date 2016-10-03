#Antonio Minondo, Keith Kinnard


import sys
import pygame
import os
from pygame.locals import *
import math
import time

from paddle import Paddle
from opponent import Opponent
from ball import Ball

from twisted.internet.defer import DeferredQueue

from twisted.internet.protocol import Factory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall


queue = DeferredQueue()

GAME_PORT = 40077

#--------------------------------------------------------------------------------
#********************************GAMESPACE***************************************
#--------------------------------------------------------------------------------   
     

class GameSpace(object):
    def __init__(self):
        #game window
        pygame.init()
        self.size = self.width, self.height = (640, 480)
        self.screen = pygame.display.set_mode(self.size)
        self.black = (0,0,0)
        
        #game scores
        self.score_p1 = 0
        self.score_p2 = 0
        
        #paddle
        self.paddle = Paddle()
        #player2 paddle
        self.opponent = Opponent()
        #ball
        self.ball = Ball()
        pygame.key.set_repeat(10,5)
        
        #opponent presses space
        self.space_host = False
        self.space_client = False
        self.direction = None
        #self.wait = False
    #helper move function
    def move(self, direction):
        if direction:
            if direction == pygame.K_UP:
                self.paddle.moveY(-2)
            if direction == pygame.K_DOWN:
                self.paddle.moveY(2)

    
    def loop(self):
        #direction = None
        win = False
        wait = False
        font = pygame.font.Font(None, 48)
        win_font = pygame.font.Font(None, 78)
        msg_font = pygame.font.Font(None, 28)
        
        #message if player waiting for opponent spacebar 
        msg = msg_font.render("waiting for opponent response", 1, (0, 200, 0))
        mrect = msg.get_rect()
        mrect.center = (320, 450)
        #render font for scores
        if(not self.ball.win):
            score1 = font.render(str(self.score_p1), 1, (200, 0, 0))
            rect1 = score1.get_rect()
            rect1.center = (250, 50)
            score2 = font.render(str(self.score_p2), 1, (0, 0, 200))
            rect2 = score2.get_rect()
            rect2.center = (380, 50)
        
        #check if someone has won
        if (self.score_p1 == 3): 
            self.winner = win_font.render("Player 1 Wins!", 1, (0, 200, 0))
            self.w_rect = self.winner.get_rect()
            self.w_rect.center = (320, 240) 
            self.msg = msg_font.render("Press spacebar to start new game", 1, (0, 200, 0))
            self.msg_rect = self.msg.get_rect()
            self.msg_rect.center = (320, 350)
            win = True
        if(self.score_p2 == 3):
            self.winner = win_font.render("Player 2 Wins!", 1, (0, 200, 0))
            self.w_rect = self.winner.get_rect()
            self.w_rect.center = (320, 240) 
            self.msg = msg_font.render("Press spacebar to start new game", 1, (0, 200, 0))
            self.msg_rect = self.msg.get_rect()
            self.msg_rect.center = (320, 350)
            win = True
            
       
        #-----------------------------------------------------------------
        #ball tick management
        #-----------------------------------------------------------------
        #move only if ball has a direction, if it doesn't have a direction it 
        #hasnt started moving
        if(self.ball.direction != None):
            mx = 5*math.sin(self.ball.ang)
            my = 5*math.cos(self.ball.ang)
            self.ball.moveX(mx)
            self.ball.moveY(my)
        
        #collide player 1
        if(self.ball.rect.colliderect(self.paddle)):
            self.ball.ang = self.ball.ang*-1
            #send data to server
            x, y = self.ball.get_center()
            info = "ball "+ str(x)+ " "+ str(y)+ " "+ str(self.ball.ang)+ " "
            queue.put(info)
        
        #collide player 2
        elif(self.ball.rect.colliderect(self.opponent)):
            self.ball.ang = self.ball.ang*-1
            #send data to server
            x, y = self.ball.get_center()
            info = "ball "+ str(x)+ " "+ str(y)+ " "+ str(self.ball.ang)+ " "
            queue.put(info)
        
        #bounds checking
        elif(self.ball.rect.centery < 15):
            self.ball.rect.centery = 15
            self.ball.ang = math.pi - self.ball.ang
            #send data to server
            x, y = self.ball.get_center()
            info = "ball "+ str(x)+ " "+ str(y)+ " "+ str(self.ball.ang)+ " "
            queue.put(info)
        elif(self.ball.rect.centery > 465):
            self.ball.rect.centery = 465
            self.ball.ang = math.pi - self.ball.ang
            #send data to server
            x, y = self.ball.get_center()
            info = "ball "+ str(x)+ " "+ str(y)+ " "+ str(self.ball.ang)+ " "
            queue.put(info)

        #user input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                reactor.stop()
            if event.type == pygame.KEYDOWN:
                self.direction = event.key
            if event.type == pygame.KEYUP:
                if (event.key == self.direction):
                    self.direction = None
             
        #move if arrow keys pressed
        if(self.direction == pygame.K_SPACE):
            self.space_host = True
            queue.put("spacebar \n")
        elif(self.space_host and self.space_client):
            print "host and client"
            #reset scores if winner
            if(self.score_p1 == 3 or self.score_p2 == 3):
                self.score_p1 = 0
                self.score_p2 = 0
                win == False
                
            #start ball movement
            self.ball.start()
            
            x, y = self.ball.get_center()

            info = "ball "+str(x)+" "+str(y)+ " "+str(self.ball.ang)+" "
            queue.put(info)
            #reset boolean variables
            self.space_host = False
            self.space_client = False
        elif(self.space_host and not self.space_client):
            print "waiting"
            wait = True
        elif(not self.space_host and self.space_client):
            print "client"
        if(self.direction != pygame.K_SPACE and self.direction != None):
            self.move(self.direction)
            #put send new coordinates of paddle to client
            x, y = self.paddle.get_center()
            info = "paddle "+str(x)+ " "+ str(y)+ " "
            queue.put(info)
            
        #check if someone scores, reset game, no data will be sent to server, both host and
        #client will check and wait 
        if(self.ball.rect.centerx < 0):
            self.score_p2 += 1
            self.paddle.rect.center = (50,240)
            self.opponent.rect.center = (600,240)
            self.ball.rect.center = (320,20)
            self.ball.direction = None
            self.space_host = False
            self.space_client = False

        if(self.ball.rect.centerx > 640):
            self.score_p1 += 1
            self.paddle.rect.center = (50,240)
            self.opponent.rect.center = (600,240)
            self.ball.rect.center = (320,20)
            self.ball.direction = None
            self.space_host = False
            self.space_client = False

        #fill in display
        self.screen.fill(self.black)
        self.screen.blit(score1, rect1)
        self.screen.blit(score2, rect2)
        if(win == True):
            self.screen.blit(self.winner, self.w_rect)
            self.screen.blit(self.msg, self.msg_rect)
        if(wait == True):
            self.screen.blit(msg, mrect)
        self.screen.blit(self.paddle.img, self.paddle.rect)
        self.screen.blit(self.opponent.img, self.opponent.rect)
        self.screen.blit(self.ball.img, self.ball.rect)
        
        pygame.display.flip()


        

 

  
#--------------------------------------------------------------------------------
#********************************SERVER******************************************
#--------------------------------------------------------------------------------   

gs = GameSpace()
            
class ServerConn(Protocol):
    def __init__(self):
        self.gs = gs
    def callback(self, data):
        self.transport.write(data)
        queue.get().addCallback(self.callback)
        
    def connectionMade(self):
        print "connected to game server"
        queue.get().addCallback(self.callback)
        #user input handling
        #send ball location and paddle location
                
    def dataReceived(self, data):
        print "received data: ", data
        #receive coordinates of player2 paddle
        data = data.split(" ")
        if(data[0] == "paddle"):
            #gs.opponent.setX(int(data[1]))
            gs.opponent.setY(int(data[2]))
        if(data[0] == "spacebar"):
            gs.space_client = True
        
    def connectionLost(self, reason):
        print "connection lost to server, ", reason
        pygame.quit()
        reactor.stop
        
class ServerConnFactory(Factory):
    def __init__(self):
        self.serverconn = ServerConn()

    def buildProtocol(self, addr):
        return self.serverconn
       
       
       
#gs = GameSpace() 
reactor.listenTCP(GAME_PORT, ServerConnFactory())
lc = LoopingCall(gs.loop)
lc.start(1/60.)
reactor.run()
