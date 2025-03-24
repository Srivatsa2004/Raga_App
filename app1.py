import streamlit as st
import pandas as pd
from myfuncs1 import load_audio, apply_noise_cancellation, detect_onsets, plot_onsets, get_onset_frequencies, match_swaras, get_shifted_swaras, find_raga

st.title("Carnatic Raga Detection")

uploaded_file = st.file_uploader("Upload an audio file", type=["opus", "wav"])
thresh = st.slider("Threshold for noise reduction", 0.0, 0.1,0.02)
if uploaded_file is not None:
    with open("temp.opus", "wb") as f:
        f.write(uploaded_file.getbuffer())

    y, sr = load_audio("temp.opus")
    y_clean = apply_noise_cancellation(y,thresh)
    onset_detect, onset_times = detect_onsets(y_clean, sr)
    onset_frequencies = get_onset_frequencies(y_clean, sr, onset_detect)
   
    
    shruthis={('C','Sa'): [261.63,523.25], ('C#','R1'): [277.18,554.37],
          ('D', 'R2/G1'): [293.66,587.33],  ('D#','R3/G2'): [311.13,622.25],
          ('E','G3'): [329.63,659.25], ('F',"M1"): [349.23,698],
          ('F#',"M2"): [369.99,739.99], ('G',"P"): [392,783],
          ('G#',"D1"): [415.3,830.61],('A',"D2/N1"): [440,880],
          ('A#',"D3/N2"): [466.16,932.68], ('B',"N3"): [246.94, 493.88, 987.77]}
    input_shruthi = st.text_input("Enter the shruthi (e.g., C, C#, D):")
    if input_shruthi:
        unique_swaras = get_shifted_swaras(onset_frequencies, shruthis, input_shruthi)

        if isinstance(unique_swaras, str): #check if get_shifted_swaras returned an error string
            st.write(unique_swaras) #display the error message
        else:
            df = pd.read_csv("Shruthi & Ragas - Raagas with names.csv")
            matched_ragas = find_raga(unique_swaras, df)

    
    plot = plot_onsets(y_clean, sr, onset_times)
    st.pyplot(plot) #add this line
    #st.write("Onset Frequencies:", onset_frequencies)
    #st.write("Swaras:", unique_swaras)
    #st.write("Matched swaras:", matched_swaras)
    #st.write("Possible Ragas:", matched_ragas)
else:
    st.write("Please enter a shruthi")
