import streamlit as st
from PIL import Image
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

def get_pdf_download_link(pdf_data, filename, text):
    pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="{filename}">{text}</a>'
    return href

def binary_to_string(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def extract_hidden_data(encoded_image_path):
    encoded_image = Image.open(encoded_image_path)
    if encoded_image.mode != 'RGB':
        encoded_image = encoded_image.convert('RGB')

    encoded_pixels = np.array(encoded_image)
    encoded_height, encoded_width, _ = encoded_pixels.shape

    binary_data = ''

    for y in range(encoded_height):
        for x in range(encoded_width):
            r, g, b = encoded_pixels[y, x][:3]
            binary_data += f'{r & 1}{g & 1}{b & 1}'

    end_of_message = '1111111111111110'
    end_index = binary_data.find(end_of_message)
    if end_index != -1:
        binary_data = binary_data[:end_index]
    else:
        raise ValueError("End of message delimiter not found!")

    # Decode the type of the hidden data
    file_type = binary_to_string(binary_data[1:9])
    binary_data = binary_data[9:]
    if file_type == 'G':
        mode = 'G'
        hidden_width = int(binary_data[:16], 2)
        hidden_height = int(binary_data[16:32], 2)
        binary_data = binary_data[32:]

        # Make sure to decode the base64 string
        hidden_base64 = binary_to_string(binary_data)
        decoded_bytes = base64.b64decode(hidden_base64)
        return decoded_bytes, mode
        
    elif file_type == 'P':
        mode = 'P'
        pdf_base64 = binary_to_string(binary_data)
        decoded_bytes = base64.b64decode(hidden_base64)
        return decoded_bytes, mode
        
    else:
        raise ValueError("Tipe file tidak dikenali saat dekoding.")

# Fungsi dekripsi gambar
def decryptPage():
    st.markdown("<h4 style='text-align: left;'>Upload Stego Image</h4>", unsafe_allow_html=True)
    stego_file = st.file_uploader('', type=['png', 'jpg', 'bmp', 'tiff'],key="decrypt")
    if stego_file is not None:
        extracted_message, mode = extract_hidden_data(stego_file)

        if mode == 'G':
            # Tampilkan gambar akhir
            st.image(extracted_message, caption='This is your hidden message')
            # Tambahkan link download
            st.markdown(get_image_download_link(extracted_message, 'result.jpg', 'Download extracted image'), unsafe_allow_html=True)

        else:
            pdf_file_path = "hidden_message.pdf"
            with open(pdf_file_path, "wb") as f:
                f.write(extracted_message)
            st.markdown(f'<embed src="{pdf_file_path}" width="800" height="600" type="application/pdf">', unsafe_allow_html=True)
            st.markdown(get_pdf_download_link(extracted_message, 'result.jpg', 'Download extracted image'), unsafe_allow_html=True)
        