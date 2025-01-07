import streamlit as st
from PIL import Image
import os
#Encontrando diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))
#Achando o caminho do icone
icon_path = os.path.join(current_dir,'.streamlit','Logo_azul_quadrada.PNG')
#Achando o caminho da logo
img_path = os.path.join(current_dir,'.streamlit','Logo_goener_colorida.png')
st.set_page_config(page_title="Goener", layout="wide",page_icon=icon_path)
# Aplicar o tema via CSS
st.markdown("""
    <style>
        :root {
            --primary-color: #6A994E;
            --background-color: #F4F4F9;
            --secondary-background-color: #A7C957;
            --text-color: #386641;
        }

        .stApp {
            background-color: var(--background-color) !important;
        }

        .stSidebar .sidebar-content {
            background-color: var(--secondary-background-color) !important;
        }

        p, .stMarkdown {
            color: var(--text-color) !important;
        }

        .stButton>button {
            color: white !important;
            background-color: var(--primary-color) !important;
        }
    </style>
""", unsafe_allow_html=True)
# Carregar a imagem com Pillow
img = Image.open(img_path)

# Redimensionar a imagem (alterando a altura e mantendo a proporção)
img = img.resize((int(img.width * (50 / img.height)), 50))  # Altura = 30 pixels

# Exibir a imagem redimensionada
st.image(img)
st.title("Análise de Ocorrência das Usinas")





