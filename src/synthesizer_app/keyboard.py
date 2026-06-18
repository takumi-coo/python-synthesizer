import pygame
import numpy as np

from . import state
from .constants import *
from .ui import LED

class Key:
    def __init__(self, pos, width, height, note, key, color):
        self.pos = pos
        self.width = width
        self.height = height
        self.note = note
        self.key = key
        self.color = color
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.sound = None
        self.pressed = False
        self.relesed = True
    
    def draw(self, screen):
        if self.pressed:
            pygame.draw.rect(screen, (150, 150, 150), self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 1)

    def update(self,octave):
        if self.pressed:
            return self.note+12*octave
        else :
            return -(self.note+12*octave)

    def handle_event(self, event,octave):
        pressed_keys = pygame.key.get_pressed()
        if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    if self.note%12==0 or self.note%12==5:
                        if not(self.rect.x+3*self.rect.w/4<event.pos[0]<self.rect.x+self.rect.w and self.rect.y < event.pos[1] <self.rect.y+2*self.rect.h/3 ):
                            self.pressed = True
                    elif self.note%12==4 or self.note%12==11:
                        if not(self.rect.x<event.pos[0]<self.rect.x+self.rect.w/4 and self.rect.y < event.pos[1] <self.rect.y+2*self.rect.h/3 ):
                            self.pressed = True
                    elif self.note%12==2 or self.note%12==7 or self.note%12==9:
                        if not((self.rect.x+3*self.rect.w/4<event.pos[0]<self.rect.x+self.rect.w and self.rect.y < event.pos[1] <self.rect.y+2*self.rect.h/3 ) or (self.rect.x<event.pos[0]<self.rect.x+self.rect.w/4 and self.rect.y < event.pos[1] <self.rect.y+2*self.rect.h/3 )):
                            self.pressed = True
                    else:
                        self.pressed = True
                
        elif event.type == pygame.MOUSEBUTTONUP:
                self.pressed = False
        if event.type ==  pygame.KEYDOWN:
            for k in self.key:
                self.pressed = pressed_keys[k]
        elif event.type ==  pygame.KEYUP:
            for k in self.key:
                self.pressed = pressed_keys[k]

        note = self.update(octave)
        return note


class Keyboard:
    def __init__(self, x, y, data, whiteW, whiteH, blackW, blackH, width, color):
        self.x=x
        self.y=y
        self.data=data
        self.whiteW=whiteW
        self.whiteH=whiteH
        self.blackW=blackW
        self.blackH=blackH
        self.width=width
        self.color=color
        self.wn=0
        self.octave=0
        self.rect=None
        self.keys=[]
        self.notes=[]
        self.pressed=[False for i in range(NOTE_MAX+OCTAVE_MAX*12+1)]
        self.time=[0 for i in range(NOTE_MAX+OCTAVE_MAX*12+1)]

    def creatKeyboard(self):
        x = self.x+self.width
        for note, key, color in self.data:
            if color == (255, 255, 255):
                self.keys.append(Key((x, self.y+self.width), self.whiteW, self.whiteH, note, key, color))
                x += self.whiteW
                self.wn+=1

        x = self.x+self.whiteW-self.blackW/2+self.width
        for note, key, color in self.data:
            if color == (0, 0, 0):
                self.keys.append(Key((x, self.y+self.width), self.blackW, self.blackH, note, key, color))
                if note % 12 == 3 or note % 12 == 10:
                    x += self.whiteW * 2
                else: 
                    x += WHITE_KEY_WIDTH

        self.rect = pygame.Rect(self.x,self.y,self.width*2+self.wn*self.whiteW,self.width+self.whiteH)

    def draw(self,screen):
        for i in range(self.width+1):
            rect = pygame.Rect(self.x-(self.width-i),self.y-(self.width-i),self.rect.w+2*(self.width-i),self.rect.h+(self.width-i))
            a = 1.0-0.3 * ((i+1)/ self.width)
            color = (self.color[0] * a, self.color[1] * a, self.color[2] * a)
            pygame.draw.rect(screen,color,rect)
        for key in self.keys:
            key.draw(screen)

    def handle_event(self, event,r):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.octave+=1
                if self.octave>OCTAVE_MAX:self.octave=OCTAVE_MAX
            elif event.key == pygame.K_DOWN:
                self.octave-=1
                if self.octave<OCTAVE_MIN:self.octave=OCTAVE_MIN

        for k in self.keys:
            note = k.handle_event(event,self.octave)
            self.pressed[abs(note)] = k.pressed
            if k.pressed:
                if not(note in self.notes):
                    self.notes.append(note)
            else:
                if -note in self.notes:
                    self.time[-note]=r
                    i = self.notes.index(-note)
                    del self.notes[i]
        return 1

class OctaveDisplay:
    def __init__(self,x,y,r,Max,Min,color,colorList,width=3) :
        self.x=x
        self.y=y
        self.r=r
        self.w=r*3*(Max-Min+1)+r
        self.h=r*6
        self.Max=Max
        self.Min=Min
        self.color=color
        self.colorList=colorList
        self.width=width
        self.rect = pygame.Rect(self.x,self.y,self.w,self.h)
        self.LEDs=[]

    def createLED(self):
        n = self.Max-self.Min+1
        x = 0
        y = self.h/3
        x+=self.r*2
        for i in range(n):
            self.LEDs.append(LED(self.x+x,self.y+y,self.r,self.colorList[i]))
            x+=self.r*3

    def draw(self,screen):
        rect = pygame.Rect(self.rect.x-self.width,self.rect.y-self.width,self.rect.w+2*self.width,self.rect.h+2*self.width)
        pygame.draw.rect(screen, (230,230,230), rect)
        pygame.draw.rect(screen, self.color, self.rect)
        for led in self.LEDs:
            led.x=self.x
            led.y=self.y
            led.draw(screen)
        value_surf = state.font.render("Low", True, (255, 255, 255))
        screen.blit(value_surf, (self.x+self.r, self.y+self.h-2*self.r))
        value_surf = state.font.render("High", True, (255, 255, 255))
        screen.blit(value_surf, (self.x+self.w-self.r*3-7, self.y+self.h-2*self.r))

    def update(self,octave):
        n = self.Max-self.Min+1
        for i in range(n):
            if octave == i - int(n/2):self.LEDs[i].onLED()
            else:self.LEDs[i].offLED()

