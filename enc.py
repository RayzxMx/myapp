import streamlit as st 
from PIL import Image
from PIL import ImageEnhance
import numpy as np
import base64
from io import BytesIO
from pdf2image import convert_from_path  
import tempfile
import os

# Fungsi untuk mendownload gambar stego ke dalam bentuk 'PNG'
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format='png')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

# Fungsi untuk menyesuaikan ukuran cover dengan ukuran message
def resize_image(cover, message):
    if message.mode != 'RGB':
        message = message.convert('RGB')
    return cover.resize(message.size)


def handlePdf(cover_file):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf.write(cover_file.read())
                cover_images = convert_from_path(temp_pdf.name, dpi=200)  # Use temporary file path
                cover = cover_images[0]
                os.remove(temp_pdf.name)  # Import os for file deletion
                return cover;



# Fungsi enkripsi gambar
def encryptPage():
    # Unggah gambar cover
    st.markdown("<h4 style='text-align: left;'>Upload Gambar Cover</h4>", unsafe_allow_html=True)
    cover_file = st.file_uploader('', type=['png', 'jpg', 'bmp'], key="cover")
    if cover_file is not None:
        cover = Image.open(cover_file)
        if cover.mode != 'RGB':
            cover = cover.convert('RGB')
        # Unggah gambar pesan
        st.markdown("<h4 style='text-align: left;'>Upload File</h4>", unsafe_allow_html=True)
        message_file = st.file_uploader('', type=['png', 'jpg', 'bmp' , 'pdf'], key="message")
        if message_file is not None:
            if message_file.type == 'application/pdf':
                message = handlePdf(message_file)
            else:
                message = Image.open(message_file)

            # Mengecek apakah gambar dalam format CMYK atau RGB
            if message.mode == 'CMYK':
                # Mengonversi ke RGB jika gambar dalam format CMYK
                message = message.convert('RGB')

            # Reduce the contrast of the message image
            # enhancer = ImageEnhance.Contrast(message)
            # message = enhancer.enhance(0.1)

            # Menyamakan ukuran gambar cover dengan gambar pesan
            cover = resize_image(cover, message)
            message = resize_image(message, cover) 

            # Ubah ke array untuk manipulasi
            cover = np.array(cover, dtype=np.uint8)
            message = np.array(message, dtype=np.uint8)

            # "Imbed" adalah jumlah bit dari gambar pesan yang akan disematkan dalam gambar sampul
            imbed = 4

            # Menggeser gambar pesan sebanyak (8 - imbed) bit ke kanan
            messageshift = np.right_shift(message, 8 - imbed)

            # Tampilkan gambar pesan hanya dengan bit yang disematkan di layar
            # Harus digeser dari LSB (bit paling rendah) ke MSB (bit paling tinggi)
            showmess = messageshift << (8-imbed)

            # Display the showmess image
            st.image(showmess, caption='This is your message image with the embedded bits')

            # Sekarang, ubah nilai bit yang disematkan menjadi nol pada gambar sampul
            coverzero = cover & ~(0b11111111 >> imbed)
         
            # Sekarang tambahkan gambar pesan dan gambar sampul
            stego = coverzero | messageshift

            stego = np.clip(stego, 0, 255)

            # Tampilkan gambar stego
            st.image(stego, caption='This is your stego image', channels='GRAY')

            # Ubah kembali array stego menjadi gambar
            stego_img = Image.fromarray(stego.astype(np.uint8))

            stego_img.save('stego.png')

            # Tambahkan link unduhan
            st.markdown(get_image_download_link(stego_img, 'stego.png', 'Download Stego Image'), unsafe_allow_html=True)
