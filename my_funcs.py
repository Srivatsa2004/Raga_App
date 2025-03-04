# my_funcs.py
import librosa
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
from collections import OrderedDict

def load_audio(file_path):
    y, sr = librosa.load(file_path)
    return y, sr
    
thresh= 0.02
def apply_noise_cancellation(y, thresh):
    return np.where(np.abs(y) < thresh, 0, y)

def detect_onsets(y, sr,thresh=0.02):
    y_clean = apply_noise_cancellation(y, thresh)
    onset_detect = librosa.onset.onset_detect(y=y_clean,sr=sr)
    onset_times = librosa.frames_to_time(onset_detect, sr=sr)
    return onset_detect, onset_times

def plot_waveform(y, sr, onset_times):
    plt.figure(figsize=(40, 4))
    librosa.display.waveshow(y, sr=sr, alpha=0.4)
    plt.vlines(onset_times, -1, 1, color='r', linestyle='--', label='Onsets')
    plt.xlabel("Times")
    plt.ylabel("Amplitude")
    plt.title("Onset Detection in waveform")
    plt.legend()
    return plt # Important: return the plot object

def compute_stft(y, sr, n_fft=2048, hop_length=512):
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    return stft, frequencies

def extract_onset_frequencies(stft, frequencies, onset_detect):
    onset_frequencies = []
    for i in onset_detect:
        magnitude_spectrum = np.abs(stft[:, i])
        max_bin = np.argmax(magnitude_spectrum)
        onset_frequency = frequencies[max_bin]
        onset_frequencies.append(onset_frequency)
    return onset_frequencies

def match_swaras(onset_frequencies, shruthis):
    match_swara = []
    for shruthi_name, shruthi_frequencies in shruthis.items():
        for frequency in onset_frequencies:
            closest_shruthi_frequency = min(shruthi_frequencies, key=lambda x: abs(frequency - x))
            if abs(frequency - closest_shruthi_frequency) <= 6:
                best_match_swara = shruthi_name[1] if isinstance(shruthi_name, tuple) else shruthi_name
                match_swara.append(best_match_swara)
    return match_swara

def shift_swaras(input_shruthi, shruthis): #removed carnatic_swaras, as not needed.
    shruthi_names = [shruthi_name[0] for shruthi_name in shruthis.keys()]
    try:
        start_index = shruthi_names.index(input_shruthi)
    except ValueError:
        return None # Return None if input is invalid.
    shifted_shruthis = {}
    carnatic_swaras = ['S', 'R1', 'G1', 'G2', 'G3', 'M1', 'M2', 'P', 'D1', 'N1', 'N2', 'N3']
    for i in range(len(shruthi_names)):
        swara_index = (i - start_index) % len(carnatic_swaras)
        shifted_shruthis[shruthi_names[i]] = carnatic_swaras[swara_index]
    return shifted_shruthis

def get_swaras_from_frequencies(onset_frequencies, shruthis, shifted_shruthis):
    """Gets swaras from onset frequencies using shruthis and shifted_shruthis."""
    swaras = []
    for frequency in onset_frequencies:
        for (shruthi_name_key, shruthi_name_val), shruthi_frequencies in shruthis.items():
            closest_shruthi_frequency = min(shruthi_frequencies, key=lambda x: abs(frequency - x))
            if abs(frequency - closest_shruthi_frequency) <= 6:
                swaras.append(shifted_shruthis[shruthi_name_key])
                break #prevent double matching
    return swaras

def map_swaras(swaras):
    swara_map = OrderedDict([
        ("R1", "R1"), ("R2", "G1"), ("R3", "G2"), ("G1", "G1"), ("G2", "G2"), ("G3", "G3"),
        ("Sa", "S"), ("Ma1", "M1"), ("Ma2", "M2"), ("Pa", "P"), ("Da1", "D1"), ("Da2", "N1"),
        ("Da3", "N2"), ("N1", "N1"), ("N2", "N2"), ("Ni3", "N3"), ("D3", "N2")
    ])

    swaras_replace = []
    for swara in swaras:
        if 'R1' in swaras:
            swara_in_mapping = next((k for k in swara_map if swara.startswith(k)), swara)
            swaras_replace.append(swara_map.get(swara_in_mapping, swara))
        elif 'R2' in swaras and swara == "R3":
            swaras_replace.append('G2')
        elif 'D1' in swaras and swara == "D2":
            swaras_replace.append('N1')
        elif 'D2' in swaras and swara == "D3":
            swaras_replace.append('N2')
        else:
            swaras_replace.append(swara)
    return swaras_replace

def order_swaras(swaras_replace, desired_order):
    ordered_swaras = list(OrderedDict.fromkeys([swara for desired_swara in desired_order for swara in swaras_replace if desired_swara in swara]))
    return ordered_swaras

def find_ragas(df, ordered_swaras):
    ordered_swaras = map_swaras(ordered_swaras)
    ordered_swaras_set = set(ordered_swaras)
    results=[]
    for index, value in df['Swaras'].items():
        cell_swaras = re.findall(r"[SRGMPDN][123]?[/]?[SRGMPDN]?[123]?", value)
        cell_swaras_set = set(cell_swaras)
        print(cell_swaras_set)
        if ordered_swaras_set.issubset(cell_swaras_set) and cell_swaras_set == ordered_swaras_set:
            #print(f"Raaga: {df.loc[index, 'Raagas']} contains the swaras {', '.join(ordered_swaras)}")
            results.append(df.loc[index, 'Raagas'])
    return results
