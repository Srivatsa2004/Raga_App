import streamlit as st
import pandas as pd
from myfuncs1 import load_audio, apply_noise_cancellation, detect_onsets, plot_onsets, get_onset_frequencies, match_swaras, get_shifted_swaras, find_raga

st.title("Carnatic Raga Detection")

uploaded_file = st.file_uploader("Upload an audio file", type=["opus", "wav"])

if uploaded_file is not None:
    with open("temp.opus", "wb") as f:
        f.write(uploaded_file.getbuffer())

    y, sr = load_audio("temp.opus")
    y_clean = apply_noise_cancellation(y)
    onset_detect, onset_times = detect_onsets(y_clean, sr)
    onset_frequencies = get_onset_frequencies(y_clean, sr, onset_detect)

    shruthis = {
    ('C', 'Sa'): [261.63, 523.25], ('C#', 'R1'): [277.18, 554],
    ('D', 'R2/G1'): [293.66, 587.33], ('D#', 'R3/G2'): [311.13, 622.25],
    ('E', 'G3'): [329.63, 659.25], ('F', "M1"): [349.23, 698],
    ('F#', "M2"): [369.99, 739.99, 1479], ('G', "P"): [392, 783],
    ('G#', "D1"): [415.3, 830.61, 1661], ('A', "D2/N1"): [440, 880, 1760],
    ('A#', "D3/N2"): [466.16, 932.68, 1864], ('B', "N3"): [246.94, 493.88, 987.77, 1975.5]
    }
     
