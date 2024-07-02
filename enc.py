import streamlit as st 
from PIL import Image
import numpy as np
import base64
from io import BytesIO
import os

# Fungsi untuk mendownload gambar stego ke dalam bentuk 'PNG'
def get_image_download_link(img, filename, text):
    buffered = BytesIO()
    img.save(buffered, format='png')
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{img_str}" download="{filename}">{text}</a>'
    return href

#Fungsi untuk menghitung kapasitas penyimpanan gambar cover
def calculate_capacity(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    width, height = image.size
    total_capacity_bits = width * height * 3
    total_capacity_bytes = total_capacity_bits // 8
    return width, height, total_capacity_bits, total_capacity_bytes

# Fungsi untuk menyesuaikan ukuran gambar hidden agar tidak melebihi ukuran gambar cover
def resize_image(input_image_path, output_image_path, new_width, new_height):
    image = Image.open(input_image_path)
    if image.mode != 'RGB':
        image = image.convert('RGB')
    resized_image = image.resize((new_width, new_height))
    resized_image.save(output_image_path)
    return new_width, new_height

def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def base64_to_image(encoded_string, output_image_path):
    decoded_bytes = base64.b64decode(encoded_string)
    with open(output_image_path, "wb") as image_file:
        image_file.write(decoded_bytes)

def pdf_to_base64(pdf_path):
    with open(pdf_path, "rb") as pdf_file:
        encoded_string = base64.b64encode(pdf_file.read()).decode('utf-8')
    return encoded_string

def base64_to_pdf(encoded_string, output_pdf_path):
    decoded_bytes = base64.b64decode(encoded_string)
    with open(output_pdf_path, "wb") as pdf_file:
        pdf_file.write(decoded_bytes)

def int_to_binary_string(number, bits):
    return format(number, f'0{bits}b')

def string_to_binary(data):
    return ''.join(format(ord(char), '08b') for char in data)

def binary_to_string(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    return ''.join(chr(int(char, 2)) for char in chars)

def encode_image(cover_image_path, input_file_path, output_image_path):
    cover_image = Image.open(cover_image_path)
    if cover_image.mode != 'RGB':
        cover_image = cover_image.convert('RGB')

    cover_pixels = np.array(cover_image)
    cover_height, cover_width, _ = cover_pixels.shape

    file_extension = os.path.splitext(input_file_path)[1].lower()
    
    if file_extension in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
        file_type = 'G'
        hidden_image = Image.open(input_file_path)
        if hidden_image.mode != 'RGB':
            hidden_image = hidden_image.convert('RGB')
        hidden_base64 = image_to_base64(input_file_path)
        
        hidden_width, hidden_height = hidden_image.size
        hidden_width_binary = int_to_binary_string(hidden_width, 16)
        hidden_height_binary = int_to_binary_string(hidden_height, 16)
        combined_binary = '0' + string_to_binary(file_type) + hidden_width_binary + hidden_height_binary + string_to_binary(hidden_base64) + '1111111111111110'  # End of message delimiter

    elif file_extension == '.pdf':
        file_type = 'P'
        pdf_base64 = pdf_to_base64(input_file_path)
        combined_binary = '0' + string_to_binary(file_type) + string_to_binary(pdf_base64) + '1111111111111110'  # End of message delimiter

    else:
        raise ValueError("Tipe file tidak didukung. Gunakan gambar dengan ekstensi .png, .jpg, .jpeg, .bmp, .gif atau PDF dengan ekstensi .pdf.")

    # Ensure the hidden data can fit within the cover image
    if len(combined_binary) > cover_height * cover_width * 3:
        raise ValueError("Ukuran data tersembunyi terlalu besar untuk disisipkan ke dalam gambar cover.")

    data_index = 0
    binary_message_length = len(combined_binary)

    for y in range(cover_height):
        for x in range(cover_width):
            if data_index < binary_message_length:
                r, g, b = cover_pixels[y, x][:3]

                r = (r & ~1) | int(combined_binary[data_index])
                data_index += 1
                if data_index < binary_message_length:
                    g = (g & ~1) | int(combined_binary[data_index])
                    data_index += 1
                if data_index < binary_message_length:
                    b = (b & ~1) | int(combined_binary[data_index])
                    data_index += 1

                cover_pixels[y, x] = [r, g, b]
    return cover_pixels
    

# Fungsi enkripsi gambar
def encryptPage():
    # Unggah gambar cover
    st.markdown("<h4 style='text-align: left;'>Upload Gambar Cover</h4>", unsafe_allow_html=True)
    cover_file = st.file_uploader('', type=['png', 'jpg', 'bmp'], key="cover")
    
    if cover_file is not None:
        cover_width, cover_height, total_capacity_bits, total_capacity_bytes = calculate_capacity(cover_file)
        # Unggah gambar pesan
        st.markdown("<h4 style='text-align: left;'>Upload File</h4>", unsafe_allow_html=True)
        message_file = st.file_uploader('', type=['png', 'jpg', 'bmp' , 'pdf'], key="message")
        if message_file is not None:
            hidden_image = Image.open(message_file)
            if hidden_image.mode == 'RGBA':
                hidden_image = hidden_image.convert('RGB')
            hidden_width, hidden_height = hidden_image.size
            hidden_aspect_ratio = hidden_width / hidden_height

            max_hidden_pixels = total_capacity_bits // 24 // 4
            new_hidden_width = int((max_hidden_pixels * hidden_aspect_ratio) ** 0.5)
            new_hidden_height = int(new_hidden_width / hidden_aspect_ratio)

            resized_hidden_image_path = 'resized_hidden_image.png'
            resize_image(message_file, resized_hidden_image_path, new_hidden_width, new_hidden_height)
            message_file = resized_hidden_image_path

            cover_pixels = encode_image(cover_file, message_file, 'encoded_image.png')
            encoded_image = Image.fromarray(cover_pixels)
            encoded_image.save('stego.png')
            # Tampilkan gambar stego
            st.image(cover_pixels, caption='This is your stego image', channels='GRAY')

            # Tambahkan link unduhan
            st.markdown(get_image_download_link(encoded_image, 'stego.png', 'Download Stego Image'), unsafe_allow_html=True)
