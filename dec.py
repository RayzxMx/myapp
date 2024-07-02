import streamlit as st
from PIL import Image
from PIL import ImageEnhance
import numpy as np
import base64
from io import BytesIO

# Fungsi untuk mendownload gambar stego ke dalam bentuk 'JPG'
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    if img.mode in ('RGBA', 'P'):  # Jika gambar memiliki alpha channel
        img = img.convert('RGB')  # Konversi ke 'RGB'
    img.save(buffered, format='JPEG')  # Gunakan 'JPEG' sebagai format penyimpanan
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/jpeg;base64,{img_str}" download="{filename}">{text}</a>'  # Use 'image/jpeg' as the MIME type
    return href

# Fungsi dekripsi gambar
def decryptPage():
    st.markdown("<h4 style='text-align: left;'>Upload Stego Image</h4>", unsafe_allow_html=True)
    stego_file = st.file_uploader('', type=['png', 'jpg', 'bmp', 'tiff'],key="decrypt")
    if stego_file is not None:
        stego = Image.open(stego_file)

        # Ubah menjadi double untuk manipulasi
        stego = np.array(stego, dtype=np.uint8)

        # Inisialisasi pesan yang diekstrak
        extracted_message = np.zeros(stego.shape, dtype=np.uint8)

        # "Imbed" adalah jumlah bit dari gambar pesan yang akan disematkan dalam gambar sampul
        imbed = 4

        # Ekstrak bit paling tidak signifikan (LSB) dari gambar stego
        for i in range(imbed):
            extracted_message = extracted_message | ((stego & (1 << i)) << (8 - imbed))

        extracted_message = Image.fromarray(extracted_message.astype('uint8'), 'RGB')

        # enhancer = ImageEnhance.Contrast(extracted_message)
        # extracted_message = enhancer.enhance(1.0)  # Increase contrast

        # Ubah ke dalam bentuk gambar seperti semula


        # Tampilkan gambar akhir
        st.image(extracted_message, caption='This is your hidden message')

        # Tambahkan link download
        st.markdown(get_image_download_link(extracted_message, 'result.jpg', 'Download extracted image'), unsafe_allow_html=True)
