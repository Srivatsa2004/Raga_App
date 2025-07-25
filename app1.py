import streamlit as st
import pandas as pd
import base64 # python library for encoding
from pathlib import Path
from myfuncs1 import (load_audio, apply_noise_cancellation, detect_onsets,
plot_onsets, get_onset_frequencies, match_swaras, get_shifted_swaras,
find_raga, get_ordinal_suffix)
import streamlit.components.v1 as components


#bg code
#background_url = "https://raw.githubusercontent.com/Srivatsa2004/Raga_App/refs/heads/main/image.jpg"  # You can change this to any valid CSS color name or hex code
background_url= "https://raw.githubusercontent.com/Srivatsa2004/Raga_App/refs/heads/main/orange%20bg.webp"


st.markdown(
    f"""
    <style>
    .stApp {{
       background-image: url("{background_url}");
        background-size: cover;
    }}
   
    </style>
    """,
    unsafe_allow_html=True
)

#for pop up text

if 'show_modal' not in st.session_state:
    st.session_state['show_modal'] = True

modal_placeholder = st.empty()

if st.session_state['show_modal']:
    with modal_placeholder.container():
        st.markdown("### Namaste! Welcome to Raaga Darshini!")
        st.write("This tool helps you identify ragas played on a keyboard (plain notes).  \nPlease use the thresh slider to adjust the noise filter ")
        close_button = st.button("Got it!", key="close_modal_button")
        if close_button:
            st.session_state['show_modal'] = False
            modal_placeholder.empty() # Clear the modal content
st.title("Raaga Darshini - The Raaga Recognizer")

uploaded_file = st.file_uploader("Upload an audio file", type=["opus", "wav", "mp3"])
thresh = st.slider("Threshold for noise reduction", 0.0)
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
    with st.form("my_actual_form"):
        input_shruthi = st.text_input("**Enter the shruthi (e.g., C, C#, D):**")
        submit = st.form_submit_button("Submit")
        if submit:
            if not input_shruthi:
                st.warning("Please Enter the shruthi:")
            else:
                unique_swaras = get_shifted_swaras(onset_frequencies, shruthis, input_shruthi)

                if isinstance(unique_swaras, str): #check if get_shifted_swaras returned an error string
                    st.write(unique_swaras) #display the error message
                else:
                    #st.write("Hi!")
                    df = pd.read_csv("Shruthi & Ragas - Raagas with names.csv")
                    matched_ragas = find_raga(unique_swaras, df)
                    #st.write("Possible ragas :", matched_ragas)
                    if matched_ragas:
                        ragas_string = ", ".join(matched_ragas)
                        st.markdown(
                            f"""
                            <div style="background-color: white; padding:10px 10px 2px 10px; border-radius: 3px;">
                                <p style="color: black;"> {ragas_string}</p>
                            </div> """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.write("No matching ragas found.")
    plot = plot_onsets(y_clean, sr, onset_times)
    st.pyplot(plot) #add this line

st.divider()
notice_text = "**© Created by Srivatsa S. Copyrights Reserved.**"
st.caption(notice_text)
