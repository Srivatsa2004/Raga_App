import streamlit as st
import my_funcs as mf
from collections import OrderedDict
import pandas as pd
# Pip install necessary packages before running the script
import subprocess
subprocess.run(['pip', 'install', '--upgrade', 'noisereduce'])
subprocess.run(['pip', 'uninstall', 'numba', '-y'])
subprocess.run(['pip', 'install', 'numba', '--force-reinstall'])
subprocess.run(['pip', 'install', '--upgrade', 'librosa'])

# Use your functions
st.title("My Raga Detection App")

# Load and process audio
y, sr = mf.load_audio("Dhenuka.opus")
y_clean = mf.apply_noise_cancellation(y)
onset_detect, onset_times = mf.detect_onsets(y_clean, sr)

# Plot waveform
mf.plot_waveform(y, sr, onset_times)

# Compute STFT
stft, frequencies = mf.compute_stft(y, sr)

# Extract onset frequencies
onset_frequencies = mf.extract_onset_frequencies(stft, frequencies, onset_detect)
#st.write(f"Filtered Onset Frequencies (Hz): {onset_frequencies}")

# Define shruthis
shruthis = {
    ('C','Sa'): [261.63,523.25], ('C#','R1'): [277.18,554],
    ('D', 'R2/G1'): [293.66,587.33],  ('D#','R3/G2'): [311.13,622.25],
    ('E','G3'): [329.63,659.25], ('F',"M1"): [349.23,698],
    ('F#',"M2"): [369.99,739.99,1479], ('G',"P"): [392,783],
    ('G#',"D1"): [415.3,830.61,1661],('A',"D2/N1"): [440,880,1760],
    ('A#',"D3/N2"): [466.16,932.68,1864], ('B',"N3"): [246.94, 493.88, 987.77,1975.5]
}

match_swara = mf.match_swaras(onset_frequencies, shruthis)
#st.write(f"Swaras associated are: {match_swara}")

# Input shruthi
input_shruthi = st.text_input("Enter the shruthi:", "C")
shifted_shruthis = mf.shift_swaras(input_shruthi, shruthis, ['S', 'R1', 'R2' or 'G1', 'R3' or' G2', 'G3', 'M1', 'M2', 'P', 'D1', 'D2' or 'N1', 'D3' or 'N2', 'N3'])

swaras = mf.map_swaras(match_swara, OrderedDict([
    ("R1", "R1"), ("R2", "G1"), ("R3", "G2"),("G1", "G1"),
    ("G2", "G2"),("G3", "G3"),("Sa", "S"), ("Ma1","M1"),("Ma2","M2"), ("Pa","P"),
    ("Da1", "D1"), ("Da2", "N1"),("Da3","N2"),("N1","N1"),("N2","N2"),
    ("Ni3","N3"),("D3","N2")
]))

ordered_swaras = mf.order_swaras(swaras, ['S','R', 'G', 'M', 'P', 'D', 'N'])
st.write(f"Shifted swaras are: {swaras}")
st.write(f"Ordered swaras: {ordered_swaras}")

# Find matching ragas
file_path = "Shruthi & Ragas - Raagas with names.csv"
df = pd.read_csv(file_path)
mf.find_ragas(df, ordered_swaras)
