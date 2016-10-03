#Antonio Minondo, Keith Kinnard

import sys
import pygame
import os
from pygame.locals import *
import math

from paddle import Paddle
from opponent import Opponent
from ball import Ball

from twisted.internet.defer import DeferredQueue
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall

queue = DeferredQueue()

GAME_PORT = 40077
GAME_HOST = '192.168.1.104'

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

    #helper move function
    def move(self, direction):
        if direction:
            if direction == pygame.K_UP:
                self.paddle.moveY(-2)
            if direction == pygame.K_DOWN:
                self.paddle.moveY(2)
        

    def loop(self):
        #print "loop"
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
            print "space"
            self.space_client = True
            #send data to server
            print "sp"
            queue.put("spacebar ")
            print "sp good"
        elif(self.space_host and self.space_client):
            #self.ball.direction = 1
            #reset scores if winner
            if(self.score_p1 == 3 or self.score_p2 == 3):
                self.score_p1 = 0
                self.score_p2 = 0
                win == False
               
           #reset boolean variables
            self.space_host = False
            self.space_client = False
        elif(self.space_client and not self.space_host):
            print "waiting"
            wait = True
        if(self.direction != pygame.K_SPACE and self.direction != None):
            self.move(self.direction)
            #put send new coordinates of paddle to client
            x, y = self.paddle.get_center()
            #print "bla"
            info = "paddle "+str(x)+ " "+ str(y)+ " "
            queue.put(info)
            #print "bla good"
        
        #-----------------------------------------------------------------
        #ball tick management
        #-----------------------------------------------------------------
        #move only if ball has a direction, if it doesn't have a direction it 
        #hasnt started moving, collisions are calculated by host
        
        if(self.ball.ang != 0.0):
            mx = 5*math.sin(self.ball.ang)
            my = 5*math.cos(self.ball.ang)
            self.ball.moveX(mx)
            self.ball.moveY(my)
            
        #check if someone scores, reset game, no data will be sent to server, both host and
        #client will check and wait 
        if(self.ball.rect.centerx < 0):
            self.score_p2 += 1
            self.paddle.rect.center = (600,240)
            self.opponent.rect.center = (50,240)
            self.ball.rect.center = (320,20)
            self.ball.direction = None
            self.space_host = False
            self.space_client = False
            self.ball.ang = 0.0
        if(self.ball.rect.centerx > 640):
            self.score_p1 += 1
            self.paddle.rect.center = (600,240)
            self.opponent.rect.center = (50,240)
            self.ball.rect.center = (320,20)
            self.ball.direction = None
            self.space_host = False
            self.space_client = False
            self.ball.ang = 0.0
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
        #self.gs = GameSpace()
        pass

    def callback(self, data):
        print data
        self.transport.write(data)
        queue.get().addCallback(self.callback)
        
    def connectionMade(self):
        print "connected to game server"
        queue.get().addCallback(self.callback)
        print "after queue.get()"
        #user input handling
        #send ball location and paddle location
                
    def dataReceived(self, data):
        print "received data: ", data
        data = data.split(" ")
        if(data[0] == "spacebar"):
            gs.space_host = True
        if (data[0] == "paddle"):
            #gs.opponent.setX(int(data[1]))
            gs.opponent.setY(int(data[2]))
        if (data[0] == "ball"):
            x = int(data[1])
            y = int(data[2])
            gs.ball.rect.center = (x, y)
            gs.ball.ang = float(data[3])
        #receive coordinates of player2 paddle
        
        
    def connectionLost(self, reason):
        print "connection lost to server, ", reason
        pygame.quit()
        reactor.stop
        
class ServerConnFactory(ClientFactory):
    def __init__(self):
        self.serverconn = ServerConn()

    def buildProtocol(self, addr):
        return self.serverconn
#gs = GameSpace()
reactor.connectTCP(GAME_HOST,GAME_PORT, ServerConnFactory())
lc = LoopingCall(gs.loop)
lc.start(1/60.)
reactor.run()
