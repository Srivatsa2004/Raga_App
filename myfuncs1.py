import librosa
import numpy as np
import matplotlib.pyplot as plt
import re
import pandas as pd
from collections import OrderedDict

def load_audio(file_path):
    y, sr = librosa.load(file_path)
    return y, sr

def apply_noise_cancellation(y, thresh=0.0):
    return np.where(np.abs(y) < thresh, 0, y)

def detect_onsets(y, sr, thresh=0.02):
    onset_detect = librosa.onset.onset_detect(y=y, sr=sr)
    onset_times = librosa.frames_to_time(onset_detect, sr=sr)
    return onset_detect, onset_times

def plot_onsets(y, sr, onset_times):
    plt.figure(figsize=(40, 4))
    librosa.display.waveshow(y, sr=sr, alpha=0.4)
    plt.vlines(onset_times, -1, 1, color='r', linestyle='--', label='Onsets')
    plt.xlabel("Times")
    plt.ylabel("Amplitude")
    plt.title("Onset Detection in waveform")
    plt.legend()
    return plt

def get_onset_frequencies(y, sr, onset_detect):
    n_fft = 2048
    hop_length = 512
    stft = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    frequencies = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
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

def get_shifted_swaras(onset_frequencies, shruthis, input_shruthi):
    shruthi_names = [shruthi_name[0] for shruthi_name in shruthis.keys()]
    try:
        start_index = shruthi_names.index(input_shruthi)
    except ValueError:
        return f"Shruthi '{input_shruthi}' not found in the dictionary."
    shifted_shruthis = {}
    carnatic_swaras = ['S', 'R1', 'R2' or 'G1', 'R3' or 'G2','G3','M1', 'M2', 'P', 'D1','D2' or 'N1', 'D3' or 'N2', 'N3']
    for i in range(len(shruthi_names)):
        swara_index = (i - start_index) % len(carnatic_swaras)
        shifted_shruthis[shruthi_names[i]] = carnatic_swaras[swara_index]
    match_swara = []
    swaras = []
    for shruthi_name, shruthi_frequencies in shruthis.items():
        for frequency in onset_frequencies:
            closest_shruthi_frequency = min(shruthi_frequencies, key=lambda x: abs(frequency - x))
            if abs(frequency - closest_shruthi_frequency) <= 6:
                shifted_swara = shifted_shruthis[shruthi_name[0]]
                match_swara.append(shifted_swara)
                swaras.append(shifted_swara)
    swara_map = OrderedDict([("R1", "R1"), ("R2", "G1"), ("R3", "G2"), ("G1", "G1"),
                                ("G2", "G2"), ("G3", "G3"), ("Sa", "S"), ("Ma1", "M1"), ("Ma2", "M2"), ("Pa", "P"),
                                ("Da1", "D1"), ("Da2", "N1"), ("Da3", "N2"), ("N1", "N1"), ("N2", "N2"),
                                ("Ni3", "N3"), ("D3", "N2")])
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
    swaras = swaras_replace
    desired_order = ['S', 'R', 'G', 'M', 'P', 'D', 'N']
    ordered_swaras = []
    for desired_swara in desired_order:
        matching_swaras = [swara for swara in swaras if desired_swara in swara and swara not in ordered_swaras]
        ordered_swaras.extend(matching_swaras)
    unique_swaras = list(OrderedDict.fromkeys(ordered_swaras))
    return unique_swaras

def find_raga(unique_swaras, df):
    ordered_swaras_set = set(unique_swaras)
    matched_ragas = []
    for index, value in df['Swaras'].items():
        cell_swaras = re.findall(r"[SRGMPDN][123]?[/]?[SRGMPDN]?[123]?", value)
        cell_swaras_set = set(cell_swaras)
        if ordered_swaras_set.issubset(cell_swaras_set) and cell_swaras_set == ordered_swaras_set:
            matched_ragas.append(f"Raaga: {df.loc[index, 'Raagas']} {', '.join(unique_swaras)}")
    return matched_ragas
