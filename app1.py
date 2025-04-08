import streamlit as st
import pandas as pd
import base64 # python library for encoding
from  pathlib import Path
from myfuncs1 import load_audio, apply_noise_cancellation, detect_onsets, plot_onsets, get_onset_frequencies, match_swaras, get_shifted_swaras, find_raga

@st.cache_data # Cache the encoding to potentially speed up reruns
def get_base64_of_bin_file(bin_file):
    """ Reads a binary file and returns its Base64 encoded string """
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

#function to set bg
def set_image_as_page_bg(image_file):
    """ Sets an image (png or jpg) as the page background """
    # Construct the file path relative to the script
    script_dir = Path(__file__).parent
    file_path = script_dir / image_filename
    try:
        # Get the file extension to set the correct MIME type
        file_extension = file_path.suffix.lower()
        mime_type = f"image/{file_extension.strip('.')}" # e.g., image/png or image/jpeg

        bin_str = get_base64_of_bin_file(str(file_path)) # Pass the full path as string
        page_bg_img = f'''
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            background-image: url("data:{mime_type};base64,{bin_str}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(0, 0, 0, 0);
        }}
        </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
        return True # Indicate success
    except FileNotFoundError:
        st.error(f"Background image file not found: {file_path}")
        return False # Indicate failure
    except Exception as e:
        st.error(f"An error occurred while setting background: {e}")
        return False # Indicate failure

# --- Your Streamlit App Code Starts Here ---

# --- SET BACKGROUND IMAGE ---
# Define the relative path to your image within the repository
# Make sure this file is committed and pushed to GitHub!
image_filename = "pic.jpg" # <<< CHANGE THIS TO YOUR IMAGE FILENAME

set_image_as_page_bg(image_filename)



st.title("Raaga Darshini - The Raaga Recognizer")

uploaded_file = st.file_uploader("Upload an audio file", type=["opus", "wav", "mp3"])
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
                    st.write("Possible ragas :", matched_ragas)
    plot = plot_onsets(y_clean, sr, onset_times)
    st.pyplot(plot) #add this line

st.divider()
notice_text = "**© Created by Srivatsa S. Copyrights Reserved.**"
st.caption(notice_text)

