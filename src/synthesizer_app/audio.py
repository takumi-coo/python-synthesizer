import pygame
import numpy as np


def Note2Frequency(note):
    return 440*pow(2,(note-69)/12)

# サイン波生成関数
def generate_sine_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = np.sin(2 * np.pi * frequency * t)
    return wave

# ノコギリ波生成関数
def generate_sawtooth_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    sawtooth_wave = (2 * (t * frequency - np.floor(0.5 + t * frequency)))
    return sawtooth_wave

# 矩形波生成関数
def generate_square_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    square_wave = np.sign(np.sin(2 * np.pi * frequency * t))
    return square_wave

# 三角波生成関数
def generate_triangle_wave(frequency, duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    triangle_wave = (2 * np.abs(2 * (t * frequency - np.floor(t * frequency + 0.5))) - 1)
    return triangle_wave

# 加算合成シンセサイザーの音を生成
def generate_additive_synth(waveform,frequency, duration, sample_rate, amps):
    combined_wave = np.zeros(int(sample_rate * duration))
    for i, amp in enumerate(amps):
        combined_wave += amp * waveform(frequency * (i + 1), duration, sample_rate)
    
    # 正規化してクリッピングを防ぐ
    max_amp = np.max(np.abs(combined_wave))
    if max_amp > 1e-8:
        combined_wave = combined_wave / max_amp
    return combined_wave

def make_sound(wave_data):
    """Convert a normalized waveform to a pygame Sound.

    The array shape must match the mixer channel count. This keeps the app
    working whether pygame is initialized as mono or stereo.
    """
    mixer_info = pygame.mixer.get_init()
    channels = mixer_info[2] if mixer_info is not None else 1
    wave_data = np.asarray(wave_data, dtype=np.float32)
    wave_data = np.clip(wave_data, -1.0, 1.0)

    if channels == 1:
        pcm = (wave_data * 32767).astype(np.int16)
    else:
        pcm = np.column_stack([wave_data] * channels)
        pcm = (pcm * 32767).astype(np.int16)

    return pygame.sndarray.make_sound(pcm)


def return_wave(note, waveform_id, width):
    f = 11 * pow(2, (note - 69) / 12)
    if waveform_id == 0:
        return generate_sine_wave(f, 1, width + 1)
    if waveform_id == 1:
        return generate_sawtooth_wave(f, 1, width + 1)
    if waveform_id == 2:
        return generate_triangle_wave(f, 1, width + 1)
    if waveform_id == 3:
        return generate_square_wave(f, 1, width + 1)
    return np.zeros(width + 1)
