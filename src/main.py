import sys
import pygame
import numpy as np

from synthesizer_app import state
from synthesizer_app.constants import *
from synthesizer_app.audio import (
    generate_sine_wave, generate_sawtooth_wave, generate_triangle_wave,
    generate_square_wave, return_wave, make_sound
)
from synthesizer_app.keyboard import Keyboard, OctaveDisplay
from synthesizer_app.ui import WindowManager, BaseBoard
from synthesizer_app.components import (
    Oscillator, Filter, ADSRenvelope, Oscilloscope, Speaker, ocsTF
)


def main(max_frames=None):
    global font, screen
    # サウンドの初期化
    pygame.mixer.pre_init(SAMPLE_RATE, MIXER_SIZE, CHANNEL, BUFFER_SIZE)
    pygame.init()

    pygame.mixer.set_num_channels(NUM_CHANNEL)

    # フォントの設定
    state.font = pygame.font.Font(None, 36)
    font = state.font      

    state.window_manager = WindowManager()
    window_manager = state.window_manager

    # 鍵盤の設定
    keydata = [
        (53, [pygame.K_z], (255, 255, 255)),           # F3
        (54, [pygame.K_s], (0, 0, 0)),                 # F#3
        (55, [pygame.K_x], (255, 255, 255)),           # G3
        (56, [pygame.K_d], (0, 0, 0)),                 # G#3
        (57, [pygame.K_c], (255, 255, 255)),           # A3
        (58, [pygame.K_f], (0, 0, 0)),                 # A#3
        (59, [pygame.K_v], (255, 255, 255)),           # B3
        (60, [pygame.K_b], (255, 255, 255)),           # C4
        (61, [pygame.K_h], (0, 0, 0)),                 # C#4
        (62, [pygame.K_n], (255, 255, 255)),           # D4
        (63, [pygame.K_j], (0, 0, 0)),                 # D#4
        (64, [pygame.K_m], (255, 255, 255)),           # E4
        (65, [pygame.K_COMMA], (255, 255, 255)),       # F4
        (66, [pygame.K_l], (0, 0, 0)),                 # F#4
        (67, [pygame.K_PERIOD], (255, 255, 255)),      # G4
        (68, [pygame.K_SEMICOLON], (0, 0, 0)),         # G#4
        (69, [pygame.K_SLASH], (255, 255, 255)),       # A4
        (70, [pygame.K_COLON, pygame.K_1], (0, 0, 0)), # A#4
        (71, [0, pygame.K_q], (255, 255, 255)),        # B4
        (72, [pygame.K_w], (255, 255, 255)),           # C5
        (73, [pygame.K_3], (0, 0, 0)),                 # C#5
        (74, [pygame.K_e], (255, 255, 255)),           # D5
        (75, [pygame.K_4], (0, 0, 0)),                 # D#5
        (76, [pygame.K_r], (255, 255, 255)),           # E5
        (77, [pygame.K_t], (255, 255, 255)),           # F5
        (78, [pygame.K_6], (0, 0, 0)),                 # F#5
        (79, [pygame.K_y], (255, 255, 255)),           # G5
        (80, [pygame.K_7], (0, 0, 0)),                 # G#5
        (81, [pygame.K_u], (255, 255, 255)),           # A5
        (82, [pygame.K_8], (0, 0, 0)),                 # A#5
        (83, [pygame.K_i], (255, 255, 255)),           # B5
        (84, [pygame.K_o], (255, 255, 255)),           # C6
        (85, [pygame.K_0], (0, 0, 0)),                 # C#5
        (86, [pygame.K_p], (255, 255, 255)),           # D5
        (87, [pygame.K_MINUS], (0, 0, 0)),             # D#5
        (88, [pygame.K_AT], (255, 255, 255)),          # E5
    ]

    # 鍵盤を生成
    keyboard = Keyboard(KEYBOARD_POS_X,KEYBOARD_POS_Y,keydata,WHITE_KEY_WIDTH,WHITE_KEY_HEIGHT,BLACK_KEY_WIDTH,BLACK_KEY_HEIGHT,5,(200,200,200))
    keyboard.creatKeyboard()

    ledColor=(250,0,0)
    knobColor=(100,100,100)
    mainsliColor=((250,125,0),(120,120,120),(200,200,200))
    subsliColor=[((250,125,0),(120,120,120),(200,200,200))]
    buttonColor=(250,0,0)
    bg=(180,180,180)
    wbg=(200,200,200)
    oscillators=[]
    for i in range(4):  
        oscillator=Oscillator(i,KEYBOARD_POS_X+(OSCILLATOR_WIDTH)*i,OSCILLATOR_POS_Y,OSCILLATOR_WIDTH,OSCILLATOR_HEIGHT,ledColor,knobColor,mainsliColor,subsliColor,buttonColor,bg,wbg)
        window_manager.add_window(oscillator)
        oscillators.append(oscillator)

    LOWPASSFILTER_POS_X = oscillators[3].rect.x+oscillators[3].rect.w+15
    LOWPASSFILTER_POS_Y = oscillators[3].rect.y
    HIGHPASSFILTER_POS_X = LOWPASSFILTER_POS_X
    HIGHPASSFILTER_POS_Y = LOWPASSFILTER_POS_Y+FILTER_HEIDHT+16

    lowpassfilter = Filter('low',LOWPASSFILTER_POS_X,LOWPASSFILTER_POS_Y,FILTER_WIDTH,FILTER_HEIDHT,(200,200,200),(230,230,230),3,"LowPass")
    highpassfilter = Filter('high',HIGHPASSFILTER_POS_X,HIGHPASSFILTER_POS_Y,FILTER_WIDTH,FILTER_HEIDHT,(200,200,200),(230,230,230),3,"HighPass")

    sounds=[None for i in range(88+OCTAVE_MAX*2+1)]

    baseboard = BaseBoard(10,10,SCR_WIDTH-20,KEYBOARD_POS_Y+WHITE_KEY_HEIGHT-15,(200,200,200))

    OCTAVEDISPLAY_POS_X = KEYBOARD_POS_X+keyboard.rect.w
    OCTAVEDISPLAY_POS_Y = OSCILLATOR_POS_Y+OSCILLATOR_HEIGHT

    #オクターブディスプレイを作成
    OCTAVE = 0
    colorList=[
        (255,0,0),
        (255,125,0),
        (0,255,0),
        (255,125,0),
        (255,0,0)
    ]
    octDisplay = OctaveDisplay(OCTAVEDISPLAY_POS_X,OCTAVEDISPLAY_POS_Y,LED_RADIUS,OCTAVE_MAX,OCTAVE_MIN,(180,180,180),colorList)
    octDisplay.x = OCTAVEDISPLAY_POS_X-octDisplay.w
    octDisplay.rect.x = OCTAVEDISPLAY_POS_X-octDisplay.w
    octDisplay.y = OCTAVEDISPLAY_POS_Y-octDisplay.h
    octDisplay.rect.y = OCTAVEDISPLAY_POS_Y-octDisplay.h
    octDisplay.createLED()

    speaker = Speaker(SPEAKER_POS_X,SPEAKER_POS_Y,SPEAKER_WIDTH,SPEAKER_HEIGHT-15,(20,20,20),(200,200,200),5,OSCILLATOR_HEIGHT,mainsliColor)

    envelope = ADSRenvelope(ENVELOPE_POS_X,ENVELOPE_POS_Y,ENVELOPE_WIDTH,ENVELOPE_HEIGHT,(200,200,200),(230,230,230),3,OSCILLATOR_HEIGHT)

    OSCILLOSCOPE_WIDTH = octDisplay.rect.w-10
    oscilloscope = Oscilloscope(OSCILLOSCOPE_POS_X,OSCILLOSCOPE_POS_Y,OSCILLOSCOPE_WIDTH,OSCILLOSCOPE_HEIGHT,5,(40,40,40),(200,200,200),(0,200,0))

    # Pygameウィンドウの設定
    state.screen = pygame.display.set_mode((SCR_WIDTH,SCR_HEIGHT))
    screen = state.screen
    pygame.display.set_caption("Piano Synthesizer")

    # メインループ
    running = True
    sound = None
    lNote = 0

    waveforms=[generate_sine_wave(4,1,OSCILLOSCOPE_WIDTH+1),generate_sawtooth_wave(4,1,OSCILLOSCOPE_WIDTH+1),generate_triangle_wave(4,1,OSCILLOSCOPE_WIDTH+1),generate_square_wave(4,1,OSCILLOSCOPE_WIDTH+1)]
    frame_count = 0
    while running:
        addwave = np.zeros(int(OSCILLOSCOPE_WIDTH+1))

        lNote = len(keyboard.notes)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            state.current_event = event
            r = envelope.handle_event(event)
            lowpassfilter.handle_event(event)
            highpassfilter.handle_event(event)
            speaker.handle_event(event)

            keyboard.handle_event(event,r)

            window_manager.handle_event(event)

        octDisplay.update(keyboard.octave)

        if ocsTF(oscillators):
            if (lNote!=len(keyboard.notes)):
                if len(keyboard.notes) != 0:
                    keyboard.notes = sorted(keyboard.notes)

                    for note in keyboard.notes:
                        if speaker.sounds[note] is None:
                            wave = np.zeros(int(SAMPLE_RATE * DURATION))
                            for osc in oscillators:
                                wave+=osc.generateWave(note)
                            wave = lowpassfilter.butterworthFilter(wave,note,SAMPLE_RATE)
                            wave = highpassfilter.butterworthFilter(wave,note,SAMPLE_RATE)
                            speaker.sounds[note] = make_sound(wave)
                            speaker.sounds[note].set_volume(1.0)
                            speaker.Channels[note].play(speaker.sounds[note],-1)

            for note in keyboard.notes:
                if speaker.sounds[note] is not None:
                    t = keyboard.time[note]
                    if keyboard.time[note] < int(len(envelope.avalue)):
                        speaker.sounds[note].set_volume(envelope.value[t])
                        keyboard.time[note]+=1
                    elif t < int(len(envelope.avalue))+int(len(envelope.dvalue)):
                        speaker.sounds[note].set_volume(envelope.value[t])
                        keyboard.time[note]+=1

            for i in range(len(keyboard.time)):
                if speaker.sounds[i] is not None:
                    t = keyboard.time[i]
                    if int(len(envelope.avalue))+int(len(envelope.dvalue)) < t < len(envelope.value):

                        speaker.sounds[i].set_volume(envelope.value[t])
                        keyboard.time[i]+=1
                        if keyboard.time[i] == len(envelope.value):
                            keyboard.time[i]=0
                            speaker.Channels[i].stop()
                            speaker.sounds[i]=None
                else:
                    keyboard.time[i]=0
                    speaker.sounds[i]=None
        else:
            for t in keyboard.time:t=0

        for note in keyboard.notes:
            for osc in oscillators:
                if osc.ledswitch.on:
                    v=osc.knobswitch.value
                    addwave += osc.mainslider.value * return_wave(note, v, OSCILLOSCOPE_WIDTH)
                    for amp in osc.subslider.amps:
                        addwave += amp * return_wave(note, v, OSCILLOSCOPE_WIDTH)

        screen.fill((170, 170, 170))

        baseboard.draw(screen)
        keyboard.draw(screen)
        octDisplay.draw(screen)
        for oscillator in oscillators:
            oscillator.drawOc(screen)
        lowpassfilter.draw(screen)
        highpassfilter.draw(screen)

        speaker.draw(screen)
        envelope.draw(screen)
        oscilloscope.draw(screen,addwave)

        for window in window_manager.windows:
            window.drawWindow(screen)

        pygame.display.flip()

        frame_count += 1
        if max_frames is not None and frame_count >= max_frames:
            running = False

    # Pygameの終了
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
