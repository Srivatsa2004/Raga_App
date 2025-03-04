# app.py
import streamlit as st
import my_funcs as mf
import pandas as pd
from collections import OrderedDict

st.title("My Raga Detection App")

# Load and process audio
y, sr = mf.load_audio("Kalyani.opus")
y_clean = mf.apply_noise_cancellation(y)
onset_detect, onset_times = mf.detect_onsets(y_clean, sr)

# Plot waveform
st.pyplot(mf.plot_waveform(y, sr, onset_times)) #st.pyplot() is used here.

# Compute STFT
stft, frequencies = mf.compute_stft(y, sr)

# Extract onset frequencies
onset_frequencies = mf.extract_onset_frequencies(stft, frequencies, onset_detect)

# Define shruthis
shruthis = {
    ('C', 'Sa'): [261.63, 523.25], ('C#', 'R1'): [277.18, 554],
    ('D', 'R2/G1'): [293.66, 587.33], ('D#', 'R3/G2'): [311.13, 622.25],
    ('E', 'G3'): [329.63, 659.25], ('F', "M1"): [349.23, 698],
    ('F#', "M2"): [369.99, 739.99, 1479], ('G', "P"): [392, 783],
    ('G#', "D1"): [415.3, 830.61, 1661], ('A', "D2/N1"): [440, 880, 1760],
    ('A#', "D3/N2"): [466.16, 932.68, 1864], ('B', "N3"): [246.94, 493.88, 987.77, 1975.5]
}

match_swara = mf.match_swaras(onset_frequencies, shruthis)

# Input shruthi
input_shruthi = st.text_input("Enter the shruthi:")
shifted_shruthis = mf.shift_swaras(input_shruthi, shruthis)

if shifted_shruthis is None:
    st.error("Invalid Shruthi Input")
else:

    swaras = mf.get_swaras_from_frequencies(onset_frequencies, shruthis, shifted_shruthis)

    swara_map = OrderedDict([
        ("R1", "R1"), ("R2", "G1"), ("R3", "G2"), ("G1", "G1"),
        ("G2", "G2"), ("G3", "G3"), ("Sa", "S"), ("Ma1", "M1"), ("Ma2", "M2"), ("Pa", "P"),
        ("Da1", "D1"), ("Da2", "N1"), ("Da3", "N2"), ("N1", "N1"), ("N2", "N2"),
        ("Ni3", "N3"), ("D3", "N2")
    ])

    swaras_replace = [swara_map.get(swara, swara) for swara in swaras] #correct way to apply swara_map

    ordered_swaras = mf.order_swaras(swaras_replace, ['S', 'R', 'G', 'M', 'P', 'D', 'N'])

    st.write(f"Ordered swaras: {ordered_swaras}")

    # Find matching ragas
    file_path = "Shruthi & Ragas - Raagas with names.csv"
    df = pd.read_csv(file_path)
    raga_results = mf.find_ragas(df, ordered_swaras) #store the result in raga_results

    if raga_results: # if result is not empty
        st.write("Detected Ragas:")
        for raga in raga_results:
            st.write(raga)
    else:
        st.write("No matching ragas found.")

    #mf.find_ragas(df, ordered_swaras)
