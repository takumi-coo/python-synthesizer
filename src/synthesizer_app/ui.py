import pygame
import numpy as np

from . import state

class Button:
    def __init__(self, window, x, y, w, h, color, width):
        self.window = window
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.width = width
        self.hovered = False
        self.clicked = False
        self.animeT = 3
        self.time = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:
                self.clicked = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.clicked and self.hovered:
                self.window.toggle_visibility()
                self.clicked = False

    def draw(self, screen):
        if self.time == 0:
            for i in range(self.width):
                a = 0.3 * ((i + 1) / self.width) + 0.7
                w = self.width - i
                color = (self.color[0] * a, self.color[1] * a, self.color[2] * a)
                rect = pygame.Rect(self.rect.left - w, self.rect.top - w, self.rect.width + 2 * w, self.rect.height + 2 * w)
                pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, self.color, self.rect)
        else:
            for i in range(self.width + 1):
                a = 0.3 * ((i + 1) / self.width) + 0.5
                w = self.width - i
                color = (self.color[0] * a, self.color[1] * a, self.color[2] * a)
                rect = pygame.Rect(self.rect.left - w, self.rect.top - w, self.rect.width + 2 * w, self.rect.height + 2 * w)
                pygame.draw.rect(screen, color, rect)

    def update(self):pass


class DraggableWindow:
    def __init__(self, p, x, y,space,w, h, color,buttonColor, width):
        self.p = p
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.width = width
        self.space = space
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.visible = False
        self.button = Button(self, x + w - 10, y + 10, 10, 10, buttonColor, 3)

    def handle_event(self, event):
        if not self.visible:
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.rect.collidepoint(event.pos):
                    mouse_x,mouse_y=event.pos
                    if not((self.rect.x+self.space<=mouse_x<=self.rect.x+self.space+self.rect.w) and (self.rect.y+self.space<=mouse_y<=self.rect.y+self.space+self.rect.h)):
                        self.dragging = True
                        self.offset_x = self.rect.x - event.pos[0]
                        self.offset_y = self.rect.y - event.pos[1]
                        self.bring_to_front()
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.rect.x = event.pos[0] + self.offset_x
                self.rect.y = event.pos[1] + self.offset_y
        
        self.button.handle_event(event)

    def draw(self, screen):
        if not self.visible:
            return
        for i in range(self.width):
            a = 0.3 * ((i + 1) / self.width) + 0.7
            w = self.width - i
            color = (self.color[0] * a, self.color[1] * a, self.color[2] * a)
            rect = pygame.Rect(self.rect.x - w, self.rect.y - w, self.rect.width + 2 * w, self.rect.height + 2 * w)
            pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, self.color, self.rect)
        self.button.rect.left, self.button.rect.top = self.rect.x + self.rect.width - 20, self.rect.top + 10
        self.button.draw(screen)

    def toggle_visibility(self):
        self.visible = not self.visible

    def bring_to_front(self):
        state.window_manager.bring_window_to_front(self.p)


class WindowManager:
    def __init__(self):
        self.windows = []
        self.buttons = []

    def add_window(self, window):
        self.windows.append(window)

    def add_button(self, button):
        self.buttons.append(button)

    def handle_event(self, event):
        for button in self.buttons:
            button.handle_event(event)
        for window in self.windows:
            window.handle_event(event)

    def draw(self, screen):
        for window in self.windows:
            window.drawWindow(screen)
        for button in self.buttons:
            button.draw(screen)

    def bring_window_to_front(self, window):
        self.windows.remove(window)
        self.windows.append(window)

class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val,color):
        self.x=x
        self.y=y
        self.lasty=y
        self.w=w
        self.h=h
        self.rect = pygame.Rect(x+w/6, y, 2*w/3, h)
        self.handle_rect = pygame.Rect(x, y-h/20 , w, h/10)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.handlecolor = color[0]
        self.verlinecolor = color[1]
        self.horlinecolor = color[2]
        self.dragging = False

    def drawScale(self,screen):
        self.rect=pygame.Rect(self.x+self.w/6, self.y, 2*self.w/3, self.h)
        pygame.draw.rect(screen,self.verlinecolor , self.rect)
        for i in range(0,11):
            pygame.draw.line(screen,self.horlinecolor,(self.x+(self.w-self.w*1.1)/2,self.y+i*self.h/10),
                             (self.x+(self.w+self.w*1.1)/2,self.y+i*self.rect.h/10))

    def drawHandle(self, screen):
        self.handle_rect=pygame.Rect(self.x, self.handle_rect.y, self.w, self.h/10)
        slot_color = (int(self.handlecolor[0]*0.7), int(self.handlecolor[1]*0.7), int(self.handlecolor[2]*0.7))
        pygame.draw.rect(screen, self.handlecolor, self.handle_rect)
        pygame.draw.line(screen,slot_color,
                         (self.handle_rect.x,self.handle_rect.y+self.handle_rect.h/2),
                         (self.handle_rect.x+self.handle_rect.w/5,self.handle_rect.y+self.handle_rect.h/2))
        pygame.draw.line(screen,slot_color,
                         (self.handle_rect.x+self.handle_rect.w-self.handle_rect.w/5,self.handle_rect.y+self.handle_rect.h/2),
                         (self.handle_rect.x+self.handle_rect.w,self.handle_rect.y+self.handle_rect.h/2))
        
    def draw(self,screen):
        if(self.y!=self.lasty):
            self.handle_rect.y+=self.y-self.lasty
        self.drawScale(screen)
        self.drawHandle(screen)
        self.lasty=self.y

    def update(self):
        event = state.current_event
        if event is None:
            return
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                new_y = max(self.y, min(event.pos[1], self.rect.bottom))
                self.handle_rect.y = new_y - self.h/20
                self.value = round(self.max_val*(1 - (new_y - self.rect.top) / 200) + self.min_val,5)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        self.update()

class Sliders:
    def __init__(self,num,x,y,w,h,n,color,colorList,turn=5,space_h=50,space_v=30):
        self.num=num
        self.x=x
        self.y=y
        self.w=w
        self.h=h
        self.n=n
        self.color=color
        self.colorList=colorList
        self.turn=turn
        self.space_h=space_h
        self.space_v=space_v
        self.text_space=20
        self.rect=pygame.Rect(x,y,(w+space_h)*turn+space_h,(h+space_v)*(int(n/(turn+1))+1)+space_v+1.5*self.text_space)
        self.sliders=[]
        self.amps=[1.0 for i in range(n)]

    def createSlider(self):
        if self.n<self.turn:
            j=0
            for i in range(self.n):
                self.sliders.append(Slider(self.x+(self.w+self.space_h)*i+self.space_h, self.y+self.space_v+self.text_space, self.w, self.h, 0.0, 1.0, 1.0,self.colorList[j]))
                j+=1
                if j+1>len(self.colorList):j=0
        else:
            k=0
            for i in range(int(self.n/self.turn)):
                for j in range(self.turn):
                    if (i==self.n/self.turn-1 and j ==self.n%self.turn-1):break
                    else:
                        self.sliders.append(Slider(self.x+(self.w+self.space_h)*j+self.space_h, self.y+(self.h+self.space_v)*i+self.space_v+self.text_space, self.w, self.h, 0.0, 1.0, 1.0,self.colorList[k]))
                        k+=1
                        if k+1>len(self.colorList):k=0

    def update(self):
        self.amps=[]
        for slider in self.sliders:
            slider.update()
            self.amps.append(slider.value)
        
    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
            for slider in self.sliders:slider.handle_event(event)
        for slider in self.sliders:
            self.amps.append(slider.value)
        self.update()

    def draw(self,screen):
        pygame.draw.rect(screen,self.color,self.rect)
        value_surf = state.font.render("Oc"+str(self.num+1), True, (230, 230, 230))
        screen.blit(value_surf, (self.rect.x+5, self.rect.y+5))
        if self.n<self.turn:
            for i in range(self.n):
                self.sliders[i].x,self.sliders[i].y=self.rect.x+(self.w+self.space_h)*i+self.space_h, self.rect.y+self.space_v+self.text_space
                self.sliders[i].draw(screen)
                value_surf = state.font.render(str(i+1), True, (230, 230, 230))
                screen.blit(value_surf, (self.sliders[i].x+self.sliders[i].rect.w/2,self.sliders[i].y+self.sliders[i].rect.h+self.space_h/4))
        else:
            for i in range(int(self.n/self.turn)):
                for j in range(self.turn):
                    if (i==self.n/self.turn-1 and j ==self.n%self.turn-1):break
                    else:
                        a=i*int(self.n/self.turn)+j
                        self.sliders[a].x,self.sliders[a].y=self.rect.x+(self.w+self.space_h)*j+self.space_h, self.rect.y+(self.h+self.space_v)*i+self.space_v+self.text_space
                        self.sliders[a].draw(screen)
                        value_surf = state.font.render(str(a+1), True, (230, 230, 230))
                        screen.blit(value_surf, (self.sliders[a].x+self.sliders[a].rect.w/2,self.sliders[a].y+self.sliders[a].rect.h+self.space_h/4))

class LED:
    def __init__(self,x,y,r,color):
        self.x=x
        self.y=y
        self.r=r
        self.color=color
        self.ellipse=pygame.Rect(self.x-self.r,self.y-self.r,2*self.r,2*self.r)
        self.on=False

    def onLED(self):
        self.on=True

    def offLED(self):
        self.on=False

    def draw(self,screen):
        if self.on:pygame.draw.ellipse(screen,self.color,self.ellipse)
        else:pygame.draw.ellipse(screen,(100,100,100),self.ellipse)

class LEDSwitch(LED):
    def __init__(self, x, y, r, color):
        super().__init__(x, y, r, color)

    def handle_event(self,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                mouse_x, mouse_y = event.pos
                if (mouse_x - self.x) ** 2 + (mouse_y - self.y) ** 2 <= (self.r)** 2:
                    if self.on:self.on=False
                    else:self.on=True

class KnobSwitch:
    def __init__(self, center, radius, width,div=0,firstvalue=0,firstangle = np.pi,Min=-100,Max=100,color=(100,100,100),bg=(70,70,70),partiton=np.pi/5):
        
        self.center = center
        self.radius = radius/1.5
        self.width = width
        self.partition = partiton
        self.angle = firstangle  # 角度 (ラジアン)
        self.rad = 0
        self.div = div
        self.value = firstvalue  # 値 (0-100)
        self.Min = Min
        self.Max = Max
        self.color=color
        self.bg=bg
        self.stop = 0
        self.dragging = False

    def draw(self, screen):
        w = self.radius*1.5
        pygame.draw.rect(screen,self.bg,pygame.Rect(self.center[0]-w,self.center[1]-w,2*w,2*w))
    
        for i in range(self.width):
            pygame.draw.circle(screen, (self.color[0]-5*(self.width-i), self.color[1]-5*(self.width-i), self.color[2]-5*(self.width-i)), self.center, self.radius-i)

        # ノブのマーカーを描画
        if self.div<3:
            marker_x = self.center[0] + (self.radius - self.width) * np.cos(self.angle+np.pi/2)
            marker_y = self.center[1] + (self.radius - self.width) * np.sin(self.angle+np.pi/2)
            pygame.draw.line(screen, (255, 255, 255), self.center, (marker_x, marker_y), 2)

            marker_x = self.center[0] + (self.radius + 2*self.width) * np.cos(self.partition+np.pi/2)
            marker_y = self.center[1] + (self.radius + 2*self.width) * np.sin(self.partition+np.pi/2)
            rect = pygame.Rect(marker_x-2,marker_y-2,4,4)
            pygame.draw.ellipse(screen, (255, 255, 255), rect)

            marker_x = self.center[0] + (self.radius + 2*self.width) * np.cos(-self.partition+np.pi/2)
            marker_y = self.center[1] + (self.radius + 2*self.width) * np.sin(-self.partition+np.pi/2)
            rect = pygame.Rect(marker_x-2,marker_y-2,4,4)
            pygame.draw.ellipse(screen, (255, 255, 255), rect)
        else :
            w=w*3/4
            for i in range(self.div):
                rad = (2*i + 1)*np.pi/self.div
                x = self.center[0] + (self.radius*1.2) * np.cos(rad+np.pi/2)
                y = self.center[1] + (self.radius*1.2) * np.sin(rad+np.pi/2)
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 2)

            for i in range(self.div):
                if self.value == i:
                    rad = (2*i + 1)*np.pi/self.div
                    break
            marker_x = self.center[0] + (self.radius - self.width) * np.cos(rad+np.pi/2)
            marker_y = self.center[1] + (self.radius - self.width) * np.sin(rad+np.pi/2)
            pygame.draw.line(screen, (255, 255, 255), self.center, (marker_x, marker_y), 2)

        pygame.draw.circle(screen,self.color, self.center, self.radius/3)

    def update(self):
        event = state.current_event
        if event is None:
            return
        if self.dragging:
            if event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                rel_x, rel_y = mouse_x - self.center[0], mouse_y - self.center[1]
                self.angle = np.arctan2(rel_y, rel_x)-np.pi/2

                self.rad = self.angle
                if self.angle < 0:
                    self.rad = 2*np.pi + self.angle

                if self.div < 3:
                    if self.stop == 0:
                        if self.rad < self.partition:
                            self.stop = 1
                        elif self.rad > 2*np.pi-self.partition:
                            self.stop = -1

                    if self.stop == 1 and (self.rad<self.partition or np.pi<self.rad<2*np.pi):
                        self.angle = self.partition
                    elif  self.stop == -1 and (0<=self.rad<np.pi or 2*np.pi-self.partition<self.rad):
                        self.angle = -self.partition
                    else:
                        self.stop = 0

                    self.rad = self.angle
                    if self.angle < 0:
                        self.rad = 2*np.pi + self.angle

                    if self.rad<0:
                        self.rad+=2*np.pi
                    if self.div<3:self.value = (self.Max-self.Min)*(self.rad-self.partition)/(2*(np.pi-self.partition))+self.Min
                    else:self.value = self.rad
                    # 角度を0-100の範囲にマッピング
                else:
                    for i in range(self.div):
                        if self.rad < 2*(i+1)*np.pi/self.div:
                            self.value = i
                            break

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                mouse_x, mouse_y = event.pos
                if (mouse_x - self.center[0]) ** 2 + (mouse_y - self.center[1]) ** 2 <= (self.radius*1.5)** 2:
                    self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左クリック
                self.dragging = False

        self.update()    

class BaseBoard:
    def __init__(self,x,y,w,h,color,t=10):
        self.color=color
        self.t=t
        self.rect = pygame.Rect(x,y,w,h)
        self.top_rect = pygame.Rect(x,y,w,h)
        self.down_rect = pygame.Rect(x,y,w,h)

    def draw(self,screen):
        for i in range(self.t):
            rect = pygame.Rect(self.rect.x-(self.t-i),self.rect.y-(self.t-i),self.rect.w+2*(self.t-i),self.rect.h+2*(self.t-i))
            a = 0.3 * ((i + 1) / self.t) + 0.7
            color = (self.color[0] * a, self.color[1] * a, self.color[2] * a)
            pygame.draw.rect(screen,color,rect)
        pygame.draw.rect(screen,self.color,self.rect)

