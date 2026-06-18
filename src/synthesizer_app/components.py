import pygame
import numpy as np
from scipy.signal import butter, lfilter, iirpeak

from . import state
from .constants import *
from .audio import (
    Note2Frequency, generate_sine_wave, generate_sawtooth_wave,
    generate_square_wave, generate_triangle_wave, generate_additive_synth, make_sound
)
from .ui import Button, DraggableWindow, Sliders, Slider, LEDSwitch, KnobSwitch

class Oscillator:
    def __init__(self,n,x,y,w,h,ledColor,kobswitchColor,mainsliderColor,subsliderColor,buttonColor,bg,windowbg) :
        self.n=n
        self.rect = pygame.Rect(x,y,w,h)
        self.ledswitch=LEDSwitch(x+w/2,y+3*h/28,w/10,ledColor)
        self.knobswitch=KnobSwitch((x+w/2,y+7*h/28),w/2,5,4,color=kobswitchColor,bg=bg)
        self.mainslider=Slider(x+w/4,y+11*h/28,w/2,4*h/7,0.0,1.0,1.0,mainsliderColor)
        self.window=DraggableWindow(self,x+w+20+50*self.n,y+50+50*self.n,SLIDERS_POS_X,0,0,windowbg,buttonColor,5)
        self.subslider=Sliders(n,self.window.rect.left+SLIDERS_POS_X,self.window.rect.top+SLIDERS_POS_Y,
                               SLIDER_WIDTH,SLIDER_HEIGHT,HARMONIC,bg,subsliderColor,turn=HARMONIC)
        self.window.rect.width=self.subslider.rect.width+self.window.space*2
        self.window.rect.height=self.subslider.rect.height+self.window.space*2
        self.subslider.createSlider()
        self.button = Button(self.window,x+17*w/20,y+h-3*w/20,w/10,w/10,bg,3)
        self.bg=bg
        self.form=generate_sine_wave
        self.objects = [self.ledswitch,self.knobswitch,self.mainslider,self.button]
        self.wave = np.zeros(int(SAMPLE_RATE * DURATION))

    def drawWindow(self,screen):
        if not self.window.visible:
            return
        self.window.draw(screen)
        self.subslider.rect.left,self.subslider.rect.top=self.window.rect.left+SLIDERS_POS_X,self.window.rect.top+SLIDERS_POS_Y
        self.subslider.draw(screen)

    def drawOc(self,screen):
        rect = pygame.Rect(self.rect.x-3,self.rect.y-3,self.rect.w+6,self.rect.h+6)
        pygame.draw.rect(screen,(230,230,230),rect)
        pygame.draw.rect(screen,self.bg,self.rect)
        value_surf = state.font.render("Osc"+str(self.n+1), True, (230, 230, 230))
        screen.blit(value_surf, (self.rect.x, self.rect.y))
        for obj in self.objects:
            obj.draw(screen)
        
    def handle_event(self,event):
        for obj in self.objects:
            obj.handle_event(event)

        if not self.window.visible:
            return
        self.subslider.handle_event(event)
        self.window.handle_event(event)

    def formChange(self):
        if self.knobswitch.value == 0:
            self.form = generate_sine_wave
        elif self.knobswitch.value == 1:
            self.form = generate_sawtooth_wave
        elif self.knobswitch.value == 2:
            self.form = generate_triangle_wave
        elif self.knobswitch.value == 3:
            self.form = generate_square_wave

    def generateWave(self,note):
        self.wave = np.zeros(int(SAMPLE_RATE * DURATION))
        if self.ledswitch.on:
            self.formChange()
            f = Note2Frequency(note)
            self.wave = generate_additive_synth(self.form,f,DURATION, SAMPLE_RATE, self.subslider.amps)
            return self.wave
        else:
            return self.wave

class Filter:
    def __init__(self,Type,x,y,w,h,color,bg,width,text):
        self.Type=Type
        self.rect = pygame.Rect(x,y,w,h)
        self.color =color
        self.bg = bg
        self.width = width
        self.font = pygame.font.Font(None, 24) 
        self.text = text
        self.ledswitch = LEDSwitch(x+w-20,y+20,10,(250,0,0))
        self.resonancefreqknobswitch = KnobSwitch((x+w/6-w/24,y+4*h/7),w/8,3,bg=self.color,firstvalue=1000.0,Max=8000.0,Min=20.0)
        self.cutoffknobswitch = KnobSwitch((x+w/3-w/36,y+h/4),w/8,3,bg=self.color,firstvalue=1000.0,Max=8000.0,Min=20.0)
        self.resonanceknobswitch = KnobSwitch((x+w/2,y+4*h/7),w/8,3,bg=self.color,firstangle=np.pi/5,firstvalue=1.00,Max=10.00,Min=1.00)
        self.orderknobswitch = KnobSwitch((x+2*w/3+w/36,y+h/4),w/8,3,bg=self.color,firstvalue=5.00,Max=10.00,Min=0.00)
        self.qualityfactorknobswitch = KnobSwitch((x+5*w/6+w/24,y+4*h/7),w/8,3,bg=self.color,firstangle=-np.pi/5,firstvalue=1.00,Max=1.00,Min=0.01)
        self.knobs=[self.resonancefreqknobswitch,self.cutoffknobswitch,self.resonanceknobswitch,self.orderknobswitch,self.qualityfactorknobswitch]
        # Cutoff / resonance are fixed Hz values and do not track played notes.
        self.knobstext = [' resHz',' cutHz','  gain ',' order','quality']

    def _get_filter_frequencies(self, sample_rate=SAMPLE_RATE):
        """Return safe fixed cutoff/resonance frequencies in Hz.

        The cutoff and resonance-frequency knobs are interpreted directly as
        Hz values, independent of the currently played note.
        """
        nyq = 0.5 * sample_rate
        cutoff = float(np.clip(self.cutoffknobswitch.value, 20.0, nyq * 0.95))
        resonance = float(np.clip(self.resonancefreqknobswitch.value, 20.0, nyq * 0.95))
        return cutoff, resonance

    def _format_hz(self, value):
        if value is None:
            return "----"
        if value >= 1000:
            return f"{value/1000:.2f}k"
        return f"{value:.0f}"

    def _draw_center_text(self, screen, text, rect, color=(0, 200, 0), size=26):
        font = pygame.font.Font(None, size)
        surf = font.render(str(text), True, color)
        text_rect = surf.get_rect(center=rect.center)
        screen.blit(surf, text_rect)

    def draw(self, screen):
        rect = pygame.Rect(self.rect.x-self.width,self.rect.y-self.width,self.rect.w+2*self.width,self.rect.h+2*self.width)
        pygame.draw.rect(screen,self.bg,rect)
        pygame.draw.rect(screen,self.color,self.rect)
        self.ledswitch.draw(screen)
        for knob in self.knobs:
            knob.draw(screen)

        value_surf = state.font.render(self.text, True, (230, 230, 230))
        screen.blit(value_surf, (self.rect.x+5, self.rect.y+5))

        for (knob,text) in zip(self.knobs,self.knobstext):
            value_surf = state.font.render(text, True, (230, 230, 230))
            x,y=knob.center[0]-knob.radius,knob.center[1]+knob.radius+5
            screen.blit(value_surf, (x, y))

        # 数値表示エリア
        rect = pygame.Rect(self.rect.x,self.rect.y+7*self.rect.h/9,self.rect.w,2*self.rect.h/9)
        color = (40,40,40)
        pygame.draw.rect(screen,color,rect)
        pygame.draw.line(screen,self.bg,(self.rect.x,self.rect.y+7*self.rect.h/9),(self.rect.x+self.rect.w,self.rect.y+7*self.rect.h/9),self.width)

        cutoff, resonance = self._get_filter_frequencies(sample_rate=SAMPLE_RATE)
        values = [
            self._format_hz(resonance),
            self._format_hz(cutoff),
            f"{self.resonanceknobswitch.value:.1f}",
            str(max(1, int(round(self.orderknobswitch.value)))),
            f"{self.qualityfactorknobswitch.value:.2f}",
        ]

        # 各セルの中央に表示
        for i, value in enumerate(values):
            cell = pygame.Rect(
                self.rect.x + i * self.rect.w / 5,
                self.rect.y + 7 * self.rect.h / 9,
                self.rect.w / 5,
                2 * self.rect.h / 9,
            )
            self._draw_center_text(screen, value, cell)

        for i in range(1,5):
            pygame.draw.line(screen,self.bg,(self.rect.x+i*self.rect.w/5,self.rect.y+7*self.rect.h/9),(self.rect.x+i*self.rect.w/5,self.rect.y+self.rect.h),self.width-2)

    def butterworthFilter(self, wave, note, sample_rate):
        if self.ledswitch.on:
            nyq = 0.5 * sample_rate
            cutoff, resonance = self._get_filter_frequencies(sample_rate)

            normal_cutoff = cutoff / nyq
            order = max(1, int(round(self.orderknobswitch.value)))
            q = max(0.01, float(self.qualityfactorknobswitch.value))

            # バターワースフィルタ
            b, a = butter(order, normal_cutoff, btype=self.Type, analog=False)

            # レゾナンス（ピーク）フィルタ
            normal_resonance = resonance / nyq
            b_res, a_res = iirpeak(normal_resonance, q)
            b_res *= self.resonanceknobswitch.value

            # 低域/高域通過フィルタとレゾナンスフィルタを組み合わせる
            b = np.convolve(b, b_res)
            a = np.convolve(a, a_res)
            wave = lfilter(b, a, wave)

        return wave
    
    def handle_event(self,event):
        self.ledswitch.handle_event(event)
        for knob in self.knobs:
            knob.handle_event(event)

class ADSRenvelope:
    def __init__(self,x,y,w,h,color,bg,width,HEIGHT):
        self.rect = pygame.Rect(x,y,w,h)
        self.color = color
        self.bg = bg
        self.width = width
        self.HEIGHT = HEIGHT
        self.font = pygame.font.Font(None, 24) 
        self.ratoknobswitch = KnobSwitch((x+w/6-w/24,y+4*h/7),w/8,3,div=0,bg=self.color,firstvalue=0.5,Max=1.0,Min=0.01)
        self.attackknobswitch = KnobSwitch((x+w/3-w/36,y+h/4),w/8,3,div=0,bg=self.color,firstvalue=0.5,Max=1.0,Min=0.01)
        self.decayknobswitch = KnobSwitch((x+w/2,y+4*h/7),w/8,3,div=0,bg=self.color,firstvalue=0.5,Max=1.0,Min=0.01)
        self.sustainknobswitch = KnobSwitch((x+2*w/3+w/36,y+h/4),w/8,3,div=0,bg=self.color,firstvalue=0.5,Max=1.0,Min=0.01)
        self.releaseknobswitch = KnobSwitch((x+5*w/6+w/24,y+4*h/7),w/8,3,div=0,bg=self.color,firstvalue=0.5,Max=1.0,Min=0.0)
        self.knobs=[self.ratoknobswitch,self.attackknobswitch,self.decayknobswitch,self.sustainknobswitch,self.releaseknobswitch]
        self.sample_rate = 20*self.ratoknobswitch.value
        self.avalue = np.linspace(0.0,1.0,int(self.attackknobswitch.value*self.sample_rate))
        self.dvalue = np.linspace(1.0,self.sustainknobswitch.value,int(self.decayknobswitch.value*self.sample_rate))
        self.rvalue = np.linspace(self.sustainknobswitch.value,0.0,int(self.releaseknobswitch.value*self.sample_rate))
        self.value = np.append(self.avalue,np.append(self.dvalue,np.append(self.sustainknobswitch.value,np.append(self.rvalue,0.0))))
        self.knobstext=['   rato','attack','decay','sustain','release']

    def drawGraph(self,x,y,h): 
        x+=self.rect.x
        y+=self.rect.y
        rect = pygame.Rect(x,y+h/2,self.rect.w,h/2)
        color = (40,40,40)
        pygame.draw.rect(state.screen,color,rect)
        pygame.draw.line(state.screen,self.bg,(x,y+h/2),(x+self.rect.w,y+h/2),self.width)
        green=(0, 200, 0)
        pygame.draw.line(state.screen,green,(x,y+13*h/24),(x+self.rect.w,y+13*h/24),self.width)
        pygame.draw.line(state.screen,green,(x,y+23*h/24),(x+self.rect.w,y+23*h/24),self.width)
        aknob,dknob,sknob,rknob =self.attackknobswitch,self.decayknobswitch,self.sustainknobswitch,self.releaseknobswitch
        a,d,s,r=(aknob.value-aknob.Min)/(aknob.Max-aknob.Min),(dknob.value-dknob.Min)/(dknob.Max-dknob.Min),(sknob.value-sknob.Min)/(sknob.Max-sknob.Min),(rknob.value-rknob.Min)/(rknob.Max-rknob.Min)
        pos=[[x+self.rect.w/22,y+23*h/24],
             [x+(1+5*a)*self.rect.w/22,y+13*h/24],
             [x+(1+5*a+5*d)*self.rect.w/22,y+(23-10*s)*h/24],
             [x+(6+5*a+5*d)*self.rect.w/22,y+(23-10*s)*h/24],
             [x+(6+5*a+5*d+5*r)*self.rect.w/22,y+23*h/24]]
        w = abs(pos[4][0]-pos[0][0])
        d = (x+self.rect.w/2)-(pos[0][0]+w/2)
        for i in range(4):
            pygame.draw.line(state.screen,green,(pos[i][0]+d,pos[i][1]),(pos[(i+1)%5][0]+d,pos[(i+1)%5][1]),self.width)

    def draw(self,screen):
        rect = pygame.Rect(self.rect.x-self.width,self.rect.y-self.width,self.rect.w+2*self.width,self.HEIGHT+2*self.width)
        pygame.draw.rect(screen,self.bg,rect)
        rect = pygame.Rect(self.rect.x,self.rect.y,self.rect.w,self.HEIGHT)
        pygame.draw.rect(screen,self.color,rect)
        for knob in self.knobs:
            knob.draw(screen)

        value_surf = state.font.render('Envelope', True, (230, 230, 230))
        screen.blit(value_surf, (self.rect.x+5, self.rect.y+5))

        for (knob,text) in zip(self.knobs,self.knobstext):
            value_surf = state.font.render(text, True, (230, 230, 230))
            x,y=knob.center[0]-knob.radius,knob.center[1]+knob.radius+5
            screen.blit(value_surf, (x, y))

        rect = pygame.Rect(self.rect.x,self.rect.y+7*self.rect.h/9,self.rect.w,2*self.rect.h/9)
        color = (40,40,40)
        pygame.draw.rect(state.screen,color,rect)
        pygame.draw.line(state.screen,self.bg,(self.rect.x,self.rect.y+7*self.rect.h/9),(self.rect.x+self.rect.w,self.rect.y+7*self.rect.h/9),self.width)

        num_font = pygame.font.Font(None, 30) 
        for i,(knob,text) in enumerate(zip(self.knobs,self.knobstext)):
            text = str(round(knob.value,2))

            if len(text)<=2:space = 8
            elif len(text)==3:space = 13
            elif len(text)==4:space = 18
            
            value_surf = num_font.render(text, True, (0, 200, 0))
            x,y=self.rect.x+(2*i+1)*self.rect.w/10-space,self.rect.y+8*self.rect.h/9-7.5
            screen.blit(value_surf, (x, y))


        for i in range(1,5):
            pygame.draw.line(state.screen,self.bg,(self.rect.x+i*self.rect.w/5,self.rect.y+7*self.rect.h/9),(self.rect.x+i*self.rect.w/5,self.rect.y+self.rect.h),self.width-2)


        self.drawGraph(0,0,self.HEIGHT)


    def updata(self):
        self.avalue = np.linspace(0.0,1.0,int(self.attackknobswitch.value*self.sample_rate))
        self.dvalue = np.linspace(1.0,self.sustainknobswitch.value,int(self.decayknobswitch.value*self.sample_rate))
        self.rvalue = np.linspace(self.sustainknobswitch.value,0.0,int(self.releaseknobswitch.value*self.sample_rate))
        self.value = np.append(self.avalue,np.append(self.dvalue,np.append(self.sustainknobswitch.value,np.append(self.rvalue,0.0))))

        return len(self.avalue)+len(self.dvalue)+1
             
    def handle_event(self,event):
        for knob in self.knobs:
            knob.handle_event(event)
        r = self.updata()
        return r

class Oscilloscope:
    def __init__(self,x,y,w,h,width,color,bg,linecolor):
        self.rect=pygame.Rect(x,y,w,h)
        self.width=width
        self.color=color
        self.bg=bg
        self.linecolor=linecolor

    def draw(self,screen,wave):
        for i in range(self.width):
            rect = pygame.Rect(self.rect.x-(self.width-i),self.rect.y-(self.width-i),self.rect.w+(self.width-i)*2,self.rect.h+(self.width-i)*2)
            a = 1-0.3*((i + 1) / self.width) 
            color = (self.bg[0] * a, self.bg[1] * a, self.bg[2] * a)
            pygame.draw.rect(state.screen,color,rect)
        pygame.draw.rect(screen,self.color,self.rect)
        x,y=self.rect.x,self.rect.y+self.rect.h/2
        pygame.draw.line(screen,(200,200,200),(x,y),(x+self.rect.w,y),1)
        if np.max(np.abs(wave)) !=0:
            for j in range(self.rect.w):
                y0 = int(2*wave[j])
                y1 = int(2*wave[j+1])
                pygame.draw.line(screen,self.linecolor,(x+j,int(y+y0)),(x+j+1,int(y+y1)),1)
        else :
            pygame.draw.line(screen,self.linecolor,(x,y),(x+self.rect.w,y),1)

class Speaker:
    def __init__(self,x,y,w,h,color,bg,width,HEIGHT,slicolor):
        self.color=color
        self.bg=bg
        self.width=width
        self.HEIGHT = HEIGHT
        self.n=100
        self.m=100
        self.rect=pygame.Rect(x+width,y+width,w-2*width,h-2*width)
        self.slider = Slider(x+w/2-w/8,y+h+30,w/4,HEIGHT-1.4*h,0.0,1.0,1.0,slicolor)
        self.sounds=[None for i in range(NOTE_MAX+OCTAVE_MAX*12+1)]
        self.Channels=[pygame.mixer.Channel(i) for i in range(NOTE_MAX+OCTAVE_MAX*12+1)]

    
    def drawSpeaker(self,screen,x,y,w,h):
        rect = pygame.Rect(x,y,w,h)
        pygame.draw.rect(screen,self.color,rect)
        rect = pygame.Rect(( x+ w/6),( y+ h/6),2* w/3,2* h/3)
        pygame.draw.ellipse(screen,(0,0,0),rect)
        rect = pygame.Rect(( x+ w/3),( y+ h/3), w/3, h/3)
        pygame.draw.ellipse(screen,(10,10,10),rect)
        rect = pygame.Rect(( x+ w/2)- w/12,( y+ h/2)- h/12, w/6, h/6)
        pygame.draw.ellipse(screen,(0,0,0),rect)
        for i in range(1,self.n):
            pygame.draw.line(screen,(40,40,40),( x, y+i* h/self.n),
                                                ( x+ w-1, y+i* h/self.n),1)
        for i in range(1,self.m):
            pygame.draw.line(screen,(40,40,40),( x+i* w/self.m, y),
                                                ( x+i* w/self.m, y+ h-1),1)

    def draw(self,screen):
        rect = pygame.Rect(self.rect.x-3,self.rect.y-3,self.rect.w+6,self.HEIGHT+6)
        color = (230,230,230)
        pygame.draw.rect(state.screen,color,rect)
        rect = pygame.Rect(self.rect.x,self.rect.y,self.rect.w,self.HEIGHT)
        color = (180,180,180)
        pygame.draw.rect(state.screen,color,rect)
        for i in range(self.width):
            rect = pygame.Rect(self.rect.x+i,self.rect.y+i,self.rect.w-i*2,self.rect.h-i*2)
            a = 1-0.3*((i + 1) / self.width) 
            color = (self.bg[0] * a, self.bg[1] * a, self.bg[2] * a)
            pygame.draw.rect(state.screen,color,rect)
        self.drawSpeaker(screen,self.rect.x+self.width,self.rect.y+self.width,self.rect.w-2*self.width,self.rect.h-2*self.width)
        self.slider.draw(screen)
        value_surf = state.font.render('LEVEL', True, (230, 230, 230))
        x,y=self.slider.rect.x-30,self.slider.rect.y+self.slider.rect.h+15
        screen.blit(value_surf, (x, y))

    def update(self):
        for c in self.Channels:
            c.set_volume(self.slider.value)

    def handle_event(self,event):
        self.slider.handle_event(event)
        self.update()

    
def ocsTF(oscs):
    TF = False
    for osc in oscs:
        if osc.ledswitch.on:
            return True
    
    return TF

