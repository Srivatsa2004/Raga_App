import streamlit as st
import pandas as pd
import numpy as np

st.title("My First Streamlit App")

st.write("Hello, Streamlit!")

# Display a DataFrame
df = pd.DataFrame({
    'Column 1': [1, 2, 3, 4],
    'Column 2': [10, 20, 30, 40]
})
st.write("Here is a simple DataFrame:")
st.write(df)

# Plot a chart
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)
st.line_chart(chart_data)

# Add a text input widget
user_input = st.text_input("Enter some text")
if st.button("Submit"):
    st.write(f"You entered: {user_input}")
