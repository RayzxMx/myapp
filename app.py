import streamlit as st 
from PIL import Image
import numpy as np
from dec import decryptPage
from enc import encryptPage

st.set_page_config(page_title="Jelo Art Studio", page_icon="🧐:", layout="wide")

# Set up the Streamlit app
st.title('Jelo Art Studio')
st.header('Apa yang mau dilakukan kali ini? 🧐')

st.write("---")

# Define tab content functions
def encrypt_tab():
    encryptPage()

def decrypt_tab():
    decryptPage()

# Create tabs
tabs = ["Enkripsi", "Dekripsi"]
selected_tab = st.radio("Mau Ngapain?", tabs)

if selected_tab == "Enkripsi":
    encrypt_tab()
else:
    decrypt_tab()
