import librosa
import numpy as np
import matplotlib.pyplot as plt
import noisereduce as nr
import re
import pandas as pd
import scipy.signal as signal
from collections import OrderedDict

def load_audio(file_path):
    return librosa.load(file_path)

def apply_noise_cancellation(y, thresh=0.00):
    return np.where(np.abs(y) < thresh, 0, y)

def detect_onsets(y, sr):
    onset_detect = librosa.onset.onset_detect(y=y, sr=sr)
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
    plt.show()

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
    best_match_swara = None
    for shruthi_name, shruthi_frequencies in shruthis.items():
        for frequency in onset_frequencies:
            closest_shruthi_frequency = min(shruthi_frequencies, key=lambda x: abs(frequency - x))
            if abs(frequency - closest_shruthi_frequency) <= 6:
                best_match_swara = shruthi_name[1] if isinstance(shruthi_name, tuple) else shruthi_name
                match_swara.append(best_match_swara)
    return match_swara

def shift_swaras(input_shruthi, shruthis, carnatic_swaras):
    shruthi_names = [shruthi_name[0] for shruthi_name in shruthis.keys()]
    start_index = shruthi_names.index(input_shruthi)
    shifted_shruthis = {}
    for i in range(len(shruthi_names)):
        swara_index = (i - start_index) % len(carnatic_swaras)
        shifted_shruthis[shruthi_names[i]] = carnatic_swaras[swara_index]
    return shifted_shruthis

def map_swaras(swaras, swara_map):
    swaras_replace = []
    for swara in swaras:
        swara_in_mapping = next((k for k in swara_map if swara.startswith(k)), swara)
        swaras_replace.append(swara_map.get(swara_in_mapping, swara))
    return swaras_replace

def order_swaras(swaras, desired_order):
    ordered_swaras = []
    for desired_swara in desired_order:
        matching_swaras = [swara for swara in swaras if desired_swara in swara and swara not in ordered_swaras]
        ordered_swaras.extend(matching_swaras)
    return list(OrderedDict.fromkeys(ordered_swaras))

def find_ragas(df, ordered_swaras):
    ordered_swaras_set = set(ordered_swaras)
    for index, value in df['Swaras'].items():
        cell_swaras = re.findall(r"[SRGMPDN][123]?[/]?[SRGMPDN]?[123]?", value)
        cell_swaras_set = set(cell_swaras)
        if ordered_swaras_set.issubset(cell_swaras_set) and cell_swaras_set == ordered_swaras_set:
            print(f"Raaga: {df.loc[index, 'Raagas']} contains the swaras {', '.join(ordered_swaras)}")
            
def read_excel_file(file_path):
    # Read the Excel file
    df = pd.read_csv("D:\Experiment audios.csv")
    return df
